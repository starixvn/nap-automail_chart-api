// See https://aka.ms/new-console-template for more information

using ConsoleApp;

Console.WriteLine("Hello, World!");

var example = new DhwlExample();
var fromDate = new DateTime(2025, 7, 7);
var toDate = new DateTime(2025, 7, 8);
for (var date = fromDate; date <= toDate; date = date.AddDays(1))
{
    await example.Test(date);
}

Console.WriteLine("Done. Press any key to exit...");