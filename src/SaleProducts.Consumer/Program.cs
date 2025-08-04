// See https://aka.ms/new-console-template for more information

using Microsoft.Extensions.Hosting;
using Wolverine;
using Wolverine.RabbitMQ;

var builder = Host.CreateDefaultBuilder(args)
                  .UseWolverine(opts =>
                  {
                      // 1. 設定訊息總管（RabbitMQ）
                      opts.UseRabbitMq(new Uri("amqp://guest:guest@localhost:5672"))
                          .AutoProvision() // 自動建立 queue / exchange
                          .UseListenerConnectionOnly(); // 只建立 Listener 連線（本程式不送訊息）

                      // 2. 監聽指定佇列
                      opts.ListenToRabbitQueue("orders")
                          .UseDurableInbox() // 建議啟用 Durable Inbox 增加可靠性
                          .ListenerCount(4); // 4 條平行 Listener 提升吞吐

                      // 3. 掃描當前組件找 Handler；如需限制可明確指定
                      opts.ApplicationAssembly = typeof(Program).Assembly;
                  });

await builder.RunConsoleAsync(); // Ctrl+C 可優雅關閉