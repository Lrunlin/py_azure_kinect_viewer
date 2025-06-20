const express = require("express");

const app = express();
const port = 3001;

const dataDir = "E:/DeskTop/python_intelligent_computed/collect/data";
app.use("/data", express.static(dataDir));

app.listen(port, () => {});
