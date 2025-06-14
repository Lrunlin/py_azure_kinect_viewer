// static-server.js
const http = require("http");
const fs = require("fs");
const path = require("path");

const port = 3001;
const staticDir = path.resolve(__dirname, "../data");

const server = http.createServer((req, res) => {
  if (req.url.startsWith("/data/")) {
    const filePath = path.join(staticDir, req.url.replace("/data/", "../../data/"));

    // 只允许png防止越权
    if (filePath.endsWith(".png") && fs.existsSync(filePath)) {
      res.writeHead(200, { "Content-Type": "image/png" });
      fs.createReadStream(filePath).pipe(res);
    } else {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not Found");
    }
  } else {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
  }
});

server.listen(port, () => {
  console.log(`原生图片服务已启动: http://localhost:${port}/`);
});
