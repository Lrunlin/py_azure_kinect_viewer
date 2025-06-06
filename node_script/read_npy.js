//? node.js读取npy 需要npm i numpy-parser
const fs = require("fs");
const numpy = require("numpy-parser");

// 读取文件
const buffer = fs.readFileSync("./data/2025-06-05/1749108863782/1749108863782_depth.npy");

// 解析为JavaScript对象
const arr = numpy.fromArrayBuffer(buffer.buffer);

console.log(JSON.stringify(arr.data));
