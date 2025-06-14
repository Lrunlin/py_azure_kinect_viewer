const express = require("express");
const path = require("path");
const compression = require("compression");
const { exec } = require("child_process");

const app = express();
const port = 3001;

// 1. 对 ./dist 静态资源开启 gzip
const distDir = path.resolve(__dirname, "../dist");
app.use(compression()); // ⚠️ 注意：需放在 dist 静态之前
app.use("/", express.static(distDir));

// 2. /data 只做静态，不做 gzip
const dataDir = path.resolve(__dirname, "../../data");
app.use(
  "/data",
  express.static(dataDir, {
    // express.static 默认不会对图片 gzip
  })
);

// 可选首页
app.get("/", (req, res) => {
  res.sendFile(path.join(distDir, "index.html"));
});

app.listen(port, () => {
  console.log(`静态资源服务已启动: http://localhost:${port}/`);
  exec(`start http://localhost:${port}/`); //启动浏览器
});
