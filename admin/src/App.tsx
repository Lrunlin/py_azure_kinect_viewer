import { useState, useEffect } from "react";
import axios from "axios";
import { Button, Divider, Input, Image, Checkbox } from "antd";
import useFetch from "./hooks/useFetch.jsx";
import PointCloudViewer from "./PointCloudViewer.tsx";

export interface RootObject {
  status: string;
  timestamp: string;
  rgb_image: string;
  depth_image: string;
  ply_file: string;
  pcd_file: string;
  json_file: string;
}

function App() {
  const [address, setAddress] = useState(localStorage.address || "http://127.0.0.1"); //接收缓存地址
  const [preview, setPreview] = useState(+(localStorage.preview == "1")); //接收缓存预览模式

  let { data, isLoading, error, refetch } = useFetch<RootObject, {}>(
    () =>
      axios
        .get(`${address}:3000/capture`, { params: { preview_mode: preview } })
        .then(res => res.data),
    {
      manual: true,
    }
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.key === " ") {
        e.preventDefault();
        refetch();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <>
      {/* 地址部分 */}
      <div className="mt-4 ml-4">
        <Input
          className="!w-[300px]"
          placeholder="Python接口请求地址"
          value={address}
          onChange={e => setAddress(e.target.value)}
        />
        {/* <Button className="ml-4" type="primary" onClick={() => setAddress(address)}>
          地址填充
        </Button> */}
      </div>
      <Divider />
      {/* 点击请求 */}
      <div className="mt-4 ml-4">
        <Checkbox
          checked={!!preview}
          onChange={e => {
            let result = +e.target.checked;
            setPreview(result);
            localStorage.preview = result.toString();
          }}
        >
          预览模式
        </Checkbox>
        <br />
        <Button className="mt-4" loading={isLoading} type="primary" onClick={() => refetch()}>
          点云保存
        </Button>
      </div>
      <Divider />
      <div className="ml-4 mb-6">时间戳： {data?.timestamp}</div>
      {data && (
        <div className="flex" style={{ alignItems: "flex-start" }} key={data.timestamp}>
          <div className="ml-4">
            <Image
              width={400}
              src={data.rgb_image}
              preview={{ maskClassName: "11", mask: <></> }}
            />
          </div>
          {(data as any).json_data && <PointCloudViewer data={(data as any).json_data} />}
        </div>
      )}
    </>
  );
}

export default App;
