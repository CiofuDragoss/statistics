using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using aplicatie_ciofuDragos.Areas.get_date.Models;
using Newtonsoft.Json;
using System.Text;
using Newtonsoft.Json.Linq;
using System.Net.Http.Headers;
using StackExchange.Redis;

namespace aplicatie_ciofuDragos.Areas.get_date.Controllers
{
    [Area("get_date")]
    public class DateController : Controller
    {
        private readonly HttpClient _httpClient;
        private readonly string baseApiUrl;
        private readonly ConnectionMultiplexer _redis;
        public DateController(IWebHostEnvironment env,ConnectionMultiplexer redis)
        {
            baseApiUrl="http://127.0.0.1:5030";
             _redis=redis;
             _httpClient=new HttpClient();
        }   
        // GET: DateController
        public ActionResult Statistici()
        {
            return View();
        }
        public IActionResult Interogare()
        {
            return View();
        }
        
        [HttpPost]



//metoda pentru a trimite fisierul nostru zip la serverul python
public async Task<IActionResult> SendToApi(IFormFile file)
{
    
    if (file == null || file.Length == 0)
    {
        return BadRequest(new { Message = "Fisierul este gol." });
    }

    try
    {
        
        var formData = new MultipartFormDataContent();

        
        var fileContent = new StreamContent(file.OpenReadStream());
            fileContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType);
            formData.Add(fileContent, "file", file.FileName);
       
        formData.Add(new StringContent(HttpContext.Session.Id), "session_id");
        var resp = await _httpClient.PostAsync(baseApiUrl + "/processZip", formData);

        
        if (resp.IsSuccessStatusCode)
        {
            var apiResponse = await resp.Content.ReadAsStringAsync();
            HttpContext.Session.SetString("zip","true");
            return Json(new { success = true, message = "Database a fost salvat cu succes"});
        }
        else
        {
            var errorR = await resp.Content.ReadAsStringAsync();
            var errorM = JsonConvert.DeserializeObject<dynamic>(errorR)?.error;
            return Json(new { success = false, message = $"Eroare in procesarea fișierului pe API-ul Python : {errorM}" });
        }
    }
    catch (Exception ex)
    {

        return StatusCode(500, new { Message = "Eroare la trimiterea fișierului: " + ex.Message });
    }
}

        [HttpPost]
        public IActionResult SaveSessionData([FromBody] Setari setari){
            
         
           if (setari.Alg==null || (!setari.Optiuni.Contains("plot") && !setari.Optiuni.Contains("csv")))
    {
        return Json(new { success = false, message = "serveru' zice ca nu!" });
    } 
        
        string jsonString = JsonConvert.SerializeObject(setari);
        HttpContext.Session.SetString("Setari", jsonString);
        
        return Json(new { success = true });
        }
        
        

public async Task<IActionResult> verifyJsonn(){
        string apiUrl = baseApiUrl+"/processJson";
        var setari=HttpContext.Session.GetString("Setari");
        if(setari==null){
            return BadRequest(new {message="nu ai salvate setari in sesiune."});
        }
            var setari_si_sessionId = new
        {
            session_id = HttpContext.Session.Id,
            settings = JsonConvert.DeserializeObject(setari)
        };
        var setari_serializate = new StringContent(
        JsonConvert.SerializeObject(setari_si_sessionId),  
        Encoding.UTF8,  
        "application/json"  
    );
    
        try{
         HttpResponseMessage response = await _httpClient.PostAsync(apiUrl, setari_serializate);
        if(response.IsSuccessStatusCode){
        string responseData = await response.Content.ReadAsStringAsync();
        return  Ok(new { success = true, data = responseData});
        }else
         {
             return BadRequest(new {message= "avem o eroare pe partea api-ului:"+response.StatusCode});
            }
        }
                catch (Exception ex)
            {
                return BadRequest(new {message="avem o eroare :"+ex.Message});
            }
        
    }



    public async Task<IActionResult> startProcessing(){
        var sessionId = HttpContext.Session.Id;
        var redisDataKey = $"Session:{sessionId}:date";
        var db = _redis.GetDatabase();
        db.KeyDelete(redisDataKey);
        Console.WriteLine(HttpContext.Session.GetString("Setari"));
        string apiUrl=baseApiUrl+"/startProcesare";
        string seshId=HttpContext.Session.Id;
        var cerere=new StringContent(seshId,System.Text.Encoding.UTF8, "text/plain");
        var response = await _httpClient.PostAsync(apiUrl, cerere);
        if (response.IsSuccessStatusCode){
            string responseApi = await response.Content.ReadAsStringAsync();
            return Ok(new{succes=true,message=responseApi});
        }
        else{
            string responseApi = await response.Content.ReadAsStringAsync();
            string eroare=JsonConvert.DeserializeObject<dynamic>(responseApi)?.error;
            return BadRequest(new{message=eroare});
        }

    }

    public async Task<IActionResult> ApiTestt(){
        string apiUrl = baseApiUrl;
        HttpResponseMessage response = await _httpClient.GetAsync(apiUrl);
        try{
        if (response.IsSuccessStatusCode){
            string responseData = await response.Content.ReadAsStringAsync();
             var data =JsonConvert.DeserializeObject<apiTest>(responseData);
             return View(data);
        }
        else
         {
            return View("Error", $"Eroare API: {response.StatusCode}");
            }
        }catch (Exception ex)
    {
        return View("Error", ex.Message);
    }
    }
    
    
    
    

    
        


    }
}
