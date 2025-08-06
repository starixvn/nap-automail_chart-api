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
        var request = ReadHouseRequest(date);
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

    private DHWLChartRequest ReadLicenseeRequest(DateTime date)
    {
        var sbFile = $"data/LicenseeSb.json";
        var totalFile = $"data/LicenseeTotal.json";
        
        var sbData = ReadJsonFile<Dictionary<string, double>>(sbFile);
        var totalData = ReadJsonFile<Dictionary<string, double>>(totalFile);

        var request = new DHWLChartRequest
        {
            SbData = FilterDictionaryByIndex(sbData,date.Day),
            TotalData = FilterDictionaryByIndex(totalData, date.Day),
            Mtd = 11622.138945100001,
            PreviousMtd = 24998.258104199987,
            DiffMtd = "-53.51%",
            Margin = 2.9494196761602573,
            PreviousMargin = 2.657537534483892,
            DiffMargin = "+10.98%",
            Title = "LICENSEE DHWL [Jul-2025]",
            MtdDate = $"2025-07-{date.Day:00}",
            PreviousMtdDate = $"2024-07-{date.Day:00}"
        };

        return request;
    }

    private DHWLChartRequest ReadHouseRequest(DateTime date)
    {
        var sbFile = $"data/HouseSb.json";
        var totalFile = $"data/HouseTotal.json";

        var sbData = ReadJsonFile<Dictionary<string, double>>(sbFile);
        var totalData = ReadJsonFile<Dictionary<string, double>>(totalFile);

        var request = new DHWLChartRequest
        {
            SbData = FilterDictionaryByIndex(sbData, date.Day),
            TotalData = FilterDictionaryByIndex(totalData, date.Day),
            Mtd = 11622.138945100001,
            PreviousMtd = 24998.258104199987,
            DiffMtd = "-53.51%",
            Margin = 2.9494196761602573,
            PreviousMargin = 2.657537534483892,
            DiffMargin = "+10.98%",
            Title = "DHWL [Jul-2025]",
            MtdDate = $"2025-07-{date.Day:00}",
            PreviousMtdDate = $"2024-07-{date.Day:00}"
        };

        return request;
    }

    public static Dictionary<string, double> FilterDictionaryByIndex(Dictionary<string, double> dict, int index)
    {
        return dict.Where(kvp => int.TryParse(kvp.Key, out int keyIndex) && keyIndex <= index)
            .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
    }
}