using System.Text;
using Newtonsoft.Json;

namespace ConsoleApp;
public class DhwlExample
{
    public async Task Test(DateTime date)
    {
        var sbData = await ReadJsonFileAsync<Dictionary<string, decimal>>($"data/sbFigure{date:yyyyMMdd}.json");

        var totalData = await ReadJsonFileAsync<Dictionary<string, decimal>>($"data/totalFigure{date:yyyyMMdd}.json");

        var month = date.ToString("MMM");
        var year = date.ToString("yyyy");

        using var httpClient = new HttpClient();
        var requestData = new
        {
            sb_data = sbData,
            total_data = totalData,
            month,
            year
        };

        var jsonContent = JsonConvert.SerializeObject(requestData);
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
            Console.WriteLine($"HTTP Error: {response.StatusCode} - {response.ReasonPhrase}");
        }
    }

    private async Task<T> ReadJsonFileAsync<T>(string filePath)
    {
        var jsonString = await File.ReadAllTextAsync(filePath);
        return JsonConvert.DeserializeObject<T>(jsonString);
    }
}