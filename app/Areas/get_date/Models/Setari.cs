using System.ComponentModel.DataAnnotations;
namespace aplicatie_ciofuDragos.Areas.get_date.Models
{
public class Setari
{
    public string Alg { get; set; }
    public List<string> Norme { get; set; }
    public int Training { get; set; }
    public int K { get; set; }
    public int Fantome { get; set; }
    public List<string> Optiuni { get; set; }

public Setari(){
    Alg="1";
    Norme=new List<string>();
    Training=30;
    K=9;
    Fantome=20;
    Optiuni=new List<string>();
}
}
}