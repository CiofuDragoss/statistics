using System.ComponentModel.DataAnnotations;
namespace aplicatie_ciofuDragos.Areas.get_date.Models
{
    public class apiTest
{
    [Required]
    public string message{get;set;}

   
    public apiTest()
    {
      message="fail";
    }
}
}