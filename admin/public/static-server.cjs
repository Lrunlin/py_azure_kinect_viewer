const http = require("http");
const fs = require("fs");
const path = require("path");
const url = require("url");

// 配置
const port = 3001;
const dataDir = "E:/DeskTop/python_intelligent_computed/collect/data";

// 创建服务器
http
  .createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    // 路径前缀必须是 /data
    if (!parsedUrl.pathname.startsWith("/data/")) {
      res.statusCode = 404;
      res.end("Not found");
      return;
    }
    // 只允许 .png 文件
    const filePath = path.join(dataDir, parsedUrl.pathname.replace("/data/", ""));
    if (!filePath.endsWith(".png")) {
      res.statusCode = 403;
      res.end("Forbidden: Only PNG images are allowed");
      return;
    }
    // 防止路径穿越
    if (!filePath.startsWith(path.normalize(dataDir))) {
      res.statusCode = 403;
      res.end("Forbidden");
      return;
    }
    fs.access(filePath, fs.constants.F_OK, err => {
      if (err) {
        res.statusCode = 404;
        res.end("File not found");
        return;
      }
      // 读取并返回文件
      res.setHeader("Content-Type", "image/png");
      const readStream = fs.createReadStream(filePath);
      readStream.pipe(res);
    });
  })
  .listen(port, () => {
    console.log(`Server running at http://localhost:${port}/data/xxx.png`);
  });
