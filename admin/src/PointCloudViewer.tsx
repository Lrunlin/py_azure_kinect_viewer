import React from "react";
import _ReactECharts from "echarts-for-react";
import "echarts-gl";

interface PointData {
  x: number;
  y: number;
  z: number;
  r: number;
  g: number;
  b: number;
}

interface PointCloudViewerProps {
  data: PointData[];
}

//? 不知道为什么 就是要断言一下  要不包总是TS类型报错
const ReactECharts = _ReactECharts as unknown as React.ComponentType<{
  option: any; // 根据实际 option 类型调整
  style?: React.CSSProperties;
}>;

const PointCloudViewer: React.FC<PointCloudViewerProps> = ({ data }) => {
  // 将点云数据映射为echarts的data格式
  const chartData = data.map(point => {
    const { x, y, z, r, g, b } = point;
    // 将rgb转成echarts要求的rgba格式
    const color = `rgb(${r}, ${g}, ${b})`;
    return {
      value: [x, y, z],
      itemStyle: {
        color,
      },
    };
  });

  const option = {
    tooltip: {
      formatter: (params: any) => {
        const [x, y, z] = params.value;
        return `x: ${x.toFixed(2)}, y: ${y.toFixed(2)}, z: ${z.toFixed(2)}`;
      },
    },
    xAxis3D: {
      type: "value",
      name: "x",
      min: -1,
      max: 1,
    },
    yAxis3D: {
      type: "value",
      name: "y",
      min: -1,
      max: 1,
    },
    zAxis3D: {
      type: "value",
      name: "z",
      min: -1,
      max: 1,
    },
    grid3D: {
      viewControl: {
        distance: 150,
        alpha: 45,
        beta: 45,
      },
    },
    series: [
      {
        type: "scatter3D",
        symbolSize: 3,
        data: chartData,
      },
    ],
    backgroundColor: "#e8e8e8",
  };

  return (
    <div style={{ height: "600px", width: "600px" }}>
      <ReactECharts option={option} style={{ height: "100%", width: "100%" }} />
    </div>
  );
};

export default PointCloudViewer;
