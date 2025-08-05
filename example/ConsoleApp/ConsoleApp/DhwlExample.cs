using System.Text;
using Newtonsoft.Json;

namespace ConsoleApp;

public class DHWLChartRequest
{
    public Dictionary<string, double> SbData { get; set; }

    public Dictionary<string, double> TotalData { get; set; }

    public double Mtd { get; set; }

    public double PreviousMtd { get; set; }

    public string DiffMtd { get; set; }

    public double Margin { get; set; }

    public double PreviousMargin { get; set; }

    public string DiffMargin { get; set; }

    public string Title { get; set; }

    public string MtdDate { get; set; }

    public string PreviousMtdDate { get; set; }
}

public class DhwlExample
{
    public async Task Test(DateTime date)
    {
        var request = ReadRequest(date);
        using var httpClient = new HttpClient();
       
        var jsonContent = JsonConvert.SerializeObject(request);
        var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

        var response = await httpClient.PostAsync("http://localhost:5000/dhwl", content);

        if (response.IsSuccessStatusCode)
        {
            var imageBytes = await response.Content.ReadAsByteArrayAsync();
            await File.WriteAllBytesAsync($"dhwl_chart{date:yyyyMMdd}.png", imageBytes);
            Console.WriteLine($"File dhwl_chart{date:yyyyMMdd}.png is created!");
        }
        else
        {
            var text = await response.Content.ReadAsStringAsync();
            Console.WriteLine($"HTTP Error: {response.StatusCode} - {response.ReasonPhrase}");
        }
    }

    private T ReadJsonFile<T>(string filePath)
    {
        var jsonString =  File.ReadAllText(filePath);
        return JsonConvert.DeserializeObject<T>(jsonString);
    }

    private DHWLChartRequest RandomRequest(int day)
    {
        var sbData = RandomData(day);
        var totalData = RandomTotal(day, sbData);
        var request = new DHWLChartRequest
        {
            SbData = sbData,
            TotalData = totalData,
            Mtd = 32.4,
            PreviousMtd = 46.0,
            DiffMtd = "-29.45",
            Margin = 4.12,
            PreviousMargin = 4.34,
            DiffMargin = "-5.07",
            Title = "LICENSEE DHWL [Jul-2025]",
            MtdDate = "2025-07-31",
            PreviousMtdDate = "2024-07-31"
        };

        return request;
    }

    private DHWLChartRequest ReadRequest(DateTime date)
    {
        var sbFile = $"data/sbFigure{date:yyyyMMdd}.json";
        var totalFile = $"data/totalFigure{date:yyyyMMdd}.json";
        if(!File.Exists(sbFile) || !File.Exists(totalFile))
        {
            return RandomRequest(date.Day);
        }

        var sbData = ReadJsonFile<Dictionary<string, double>>(sbFile);
        var totalData = ReadJsonFile<Dictionary<string, double>>(totalFile);

        var request = new DHWLChartRequest
        {
            SbData = sbData,
            TotalData = totalData,
            Mtd = 32.4,
            PreviousMtd = 46.0,
            DiffMtd = "-29.45",
            Margin = 4.12,
            PreviousMargin = 4.34,
            DiffMargin = "-5.07",
            Title = "LICENSEE DHWL [Jul-2025]",
            MtdDate = "2025-07-31",
            PreviousMtdDate = "2024-07-31"
        };

        return request;
    }

    private Dictionary<string, double> RandomData(int day)
    {
        var random = new Random(DateTime.Now.Millisecond);
        var dict = new Dictionary<string, double>();
        for (var i = 1; i <= day; i++)
        {
            dict[i.ToString()] = (double)(random.Next(3000,7000));
        }

        return dict;
    }

    private static Dictionary<string, double> RandomTotal(int day, Dictionary<string, double> sbData)
    {
        var totalData = new Dictionary<string, double>(sbData);
        for (var i = 1; i <= day; i++)
        {
            totalData[i.ToString()] += (double)(i % 2 == 0 ? 500 : 1000); // Simulate some variation
        }

        return totalData;
    }
}