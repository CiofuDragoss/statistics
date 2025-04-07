using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

public class FileCleanupService: IHostedService, IDisposable
{

    private readonly ILogger<FileCleanupService>? _logger;
    private Timer _timer;
    private readonly string _folderPath=Path.Combine(Directory.GetCurrentDirectory(), "wwwroot");

    private readonly TimeSpan _expirationTime=TimeSpan.FromMinutes(30);

    public FileCleanupService(ILogger<FileCleanupService> logger){
        _logger=logger;

    }

    public Task StartAsync(CancellationToken cancelToken){

        _logger.LogInformation("FileCleanupService a pornit.");

        _timer = new Timer(CleanupFiles, null, TimeSpan.Zero, TimeSpan.FromMinutes(10));
        return Task.CompletedTask;
    }

    public void CleanupFiles(object state){

        try{
            if(Directory.Exists(_folderPath)){
                var files=Directory.GetDirectories(_folderPath,"server_temp*");
                foreach (string dir in files){
                     var dirInfo = new DirectoryInfo(dir);
                      if (DateTime.Now - dirInfo.LastWriteTime > _expirationTime )
                    {
                        Directory.Delete(dir, true);
                        _logger.LogInformation($"Director expirat șters: {dir}");
                    }
                }

            }
        }catch (Exception ex){
            _logger.LogError(ex, "Eroare la curatarea fisierelor");
        }
    }

      public Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("FileCleanupService se oprește.");
        
        _timer?.Change(Timeout.Infinite, 0);
        return Task.CompletedTask;
    }
public void Dispose()
    {
        _timer?.Dispose();
    }


}