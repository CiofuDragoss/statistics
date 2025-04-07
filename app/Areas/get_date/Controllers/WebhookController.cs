using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using aplicatie_ciofuDragos.Areas.get_date.Models;
using Newtonsoft.Json;
using System.Text;
using Newtonsoft.Json.Linq;
using System.Net.Http.Headers;
using Microsoft.AspNetCore.SignalR;
using aplicatie_ciofuDragos.Areas.get_date.Hubs;
using System.Text.Json.Nodes;
using Microsoft.Extensions.Caching.Distributed;
using StackExchange.Redis;
using Microsoft.AspNetCore.Mvc.ModelBinding.Binders;
using Microsoft.AspNetCore.Routing.Constraints;
using System.IO.Compression;
namespace aplicatie_ciofuDragos.Areas.get_date.Controllers
{
    
    [Area("get_date")]
    public class WebhookController : Controller
    {
        private readonly ConnectionMultiplexer _redis;
        private readonly IHubContext<NotificationHub> _hubContext;

        public WebhookController(IHubContext<NotificationHub> hubContext,ConnectionMultiplexer redis)
        {
            _hubContext = hubContext;
            _redis = redis;
        }
       [HttpGet]
    public IActionResult grafice()
    {
        var sessionId = HttpContext.Session.Id;
        var redisDataKey = $"Session:{sessionId}:date";
        var db = _redis.GetDatabase();
        var date=db.StringGet(redisDataKey);

        if(string.IsNullOrEmpty(date)){
            return View(null);
        }
        Console.WriteLine("AVEM DATE!");
        
        var dateModel = JsonConvert.DeserializeObject<dateApi>(date);
    
        
        return View(dateModel);
    }
        [HttpPost]
        public IActionResult SaveConnectionId([FromBody] ConId con_id)
{   
    var sessionId=HttpContext.Session.Id;
    var db = _redis.GetDatabase();
    var redisKey = $"Session:{sessionId}:signalR";
    db.StringSet(redisKey, con_id.idd);
    if(con_id==null || string.IsNullOrEmpty(con_id.idd)){
        return BadRequest("Eroare,nu ai con_id!");
    }
    return Ok("ConnectionId salvat în sesiune.");
}

[HttpGet]
public IActionResult DownloadCSV()
{
    Console.WriteLine("yoo");
    var sessionId = HttpContext.Session.Id;
    var redisDataKey = $"Session:{sessionId}:date";
    var db = _redis.GetDatabase();
    var date = db.StringGet(redisDataKey);

    if (string.IsNullOrEmpty(date))
    {
        return BadRequest(new { error ="Nu ati facut nici o cerere de procesare! Faceti o cerere pentru a putea descarca fisiere CSV!"});
    }

    var dateModel = JsonConvert.DeserializeObject<dateApi>(date);
    if(dateModel.path_csv==null){
        return BadRequest(new { error = "Nu ati selectat opțiunea CSV!" });
    }
    try
    {
        Console.WriteLine("am primit call in d_csv");
        var ZipPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", Path.GetDirectoryName(dateModel.path_csv[0]));
        var ZipStream = new MemoryStream();

        try
        {
            using (var archive = new ZipArchive(ZipStream, ZipArchiveMode.Create, true)){
           
                foreach (var filePath in dateModel.path_csv)
                {
                    Console.WriteLine("Adaugam: "+filePath);
                    archive.CreateEntryFromFile(Path.Combine(ZipPath,Path.GetFileName(filePath)), Path.GetFileName(filePath));
                }
            }

            
            ZipStream.Seek(0, SeekOrigin.Begin);

           
            return File(ZipStream, "application/zip", "CSVfiles.zip");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error creating zip: {ex.Message}");
            return StatusCode(500,new {error= "Eroare Interna, genereaza din nou rezultatele.."});
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
        return StatusCode(500, new {error= "Eroare Interna, genereaza din nou rezultatele.."});
    }
}

[HttpGet]
public IActionResult DownloadGrafice()
{
    var sessionId = HttpContext.Session.Id;
    var redisDataKey = $"Session:{sessionId}:date";
    var db = _redis.GetDatabase();
    var date = db.StringGet(redisDataKey);

    if (string.IsNullOrEmpty(date))
    {
        return BadRequest(new { error = "Nu ati procesat date! Faceti o cerere pentru a putea descarca grafice!" });
    }

    var dateModel = JsonConvert.DeserializeObject<dateApi>(date);
    if(dateModel.path_grafice==null){
        return BadRequest(new { error = "Nu ati selectat optiunea Plot!" });
    }
    try
    {
        Console.WriteLine("am primit call in salvare plot");
        var ZipPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", Path.GetDirectoryName(dateModel.path_grafice[0]));
        var ZipStream = new MemoryStream();

        try
        {
            using (var archive = new ZipArchive(ZipStream, ZipArchiveMode.Create, true)){
           
                foreach (var filePath in dateModel.path_grafice)
                {
                    Console.WriteLine("Adaugam: "+Path.Combine(ZipPath,Path.GetFileName(filePath)));
                    archive.CreateEntryFromFile(Path.Combine(ZipPath,Path.GetFileName(filePath)), Path.GetFileName(filePath));
                }
            }

            
            ZipStream.Seek(0, SeekOrigin.Begin);

           
            return File(ZipStream, "application/zip", "graficefiles.zip");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error creating zip: {ex.Message}");
            return StatusCode(500, "Eroare Interna, genereaza din nou rezultatele..");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
        return StatusCode(500, "Eroare Interna, genereaza din nou rezultatele..");
    }
}

[HttpPost]
public async Task<IActionResult> proc_grafice([FromBody] dateApi date)
{
    
    var sessionId = Request.Cookies["ASP.NET_SessionId"];
    Console.WriteLine("Asta este sessionul din cookie:"+sessionId);
    var redisKey = $"Session:{sessionId}:signalR";
    var dateKey=$"Session:{sessionId}:date";
    var db = _redis.GetDatabase();
    var savedSignalR = db.StringGet(redisKey);
    if(date.path_csv!=null && date.path_grafice!=null){
    List<string> path_grafice_updated=[];
    List<string> path_csv_updated=[];
    
    foreach(string path in date.path_grafice){
             string[] pathParts = path.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
             path_grafice_updated.Add(Path.Combine(pathParts[^2], pathParts[^1]).Replace("\\", "/"));
        }
        foreach(string path in date.path_csv){
            string[] pathParts = path.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            path_csv_updated.Add(Path.Combine(pathParts[^2], pathParts[^1]).Replace("\\", "/"));
        }
    date.path_csv=path_csv_updated;
    date.path_grafice=path_grafice_updated;
    }
    var dateSerialized=JsonConvert.SerializeObject(date);
    db.StringSet(dateKey,dateSerialized,TimeSpan.FromMinutes(40));
    await _hubContext.Clients.Client(savedSignalR).SendAsync("mesaj", "ready");
    db.KeyDelete(redisKey);
    return Ok("Notificare succes.");
}
    }
    }