import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button, Divider, Input, Image, Checkbox, Alert } from "antd";
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

export interface CountRootObject {
  status: string;
  date: string;
  folder_count: number;
}

export interface ResourceRootObject {
  cpu_percent: number;
  memory_mb: number;
}

function App() {
  const [address, setAddress] = useState(localStorage.address || "http://127.0.0.1"); //接收缓存地址
  const [preview, setPreview] = useState(+(localStorage.preview == "1")); //接收缓存预览模式
  const [isPreview, setIsPreview] = useState(+(localStorage.is_preview == "1")); //接收缓存预览模式
  const streamID = useRef(Date.now().toString());

  // 请求
  let { data, isLoading, error, refetch } = useFetch<RootObject, {}>(
    () =>
      axios
        .get(`${address}:3000/capture`, { params: { preview_mode: preview } })
        .then(res => res.data),
    {
      manual: true,
      callback: () => {
        setData(val => {
          if (val) {
            return { ...val, folder_count: val?.folder_count + 1 || 0 } as CountRootObject;
          } else {
            return val;
          }
        });
      },
    }
  );

  // 今日个数
  let {
    data: count,
    isLoading: countISLoading,
    setData,
  } = useFetch<CountRootObject, {}>(() => axios.get(`${address}:3000/stats`).then(res => res.data));

  // 绑定空格键
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

  // 资源占用 5秒更新
  let { data: resource, refetch: resourceRefetch } = useFetch<ResourceRootObject, {}>(
    () => axios.get(`${address}:3000/resource`).then(res => res.data),
    {
      callback: () => {
        setTimeout(() => {
          resourceRefetch();
        }, 5000);
      },
    }
  );

  return (
    <>
      <Alert
        className="!mx-4 !mt-4"
        message={
          <div className="flex">
            <div className="flex">
              今日采集个数: <div className="font-bold mx-1">{count?.folder_count || 0}</div> 个
            </div>
            {resource && (
              <div className="ml-8 flex">
                <div className="flex">
                  CPU:<span className="font-bold">{resource?.cpu_percent}%</span>
                </div>
                <div className="ml-4 flex">
                  内存:<span className="font-bold">{resource?.memory_mb}MB</span>
                </div>
              </div>
            )}
          </div>
        }
        type="info"
        showIcon
      />
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
        <div>
          <Checkbox
            checked={!!preview}
            onChange={e => {
              let result = +e.target.checked;
              setPreview(result);
              localStorage.preview = result.toString();
            }}
          >
            预览点云
          </Checkbox>
          <Checkbox
            checked={!!isPreview}
            onChange={e => {
              if (isPreview) {
                axios.get(`${address}:3000/close_stream`, {
                  params: { stream_id: streamID.current },
                });
              }
              let result = +e.target.checked;
              streamID.current = Date.now().toString();
              setIsPreview(result);
              localStorage.is_preview = result.toString();
            }}
          >
            实时画面
          </Checkbox>
        </div>
        <div>
          <Button className="mt-4" loading={isLoading} type="primary" onClick={() => refetch()}>
            点云保存
          </Button>
        </div>
      </div>
      <Divider />
      <div className="ml-4 mb-6">时间戳： {data?.timestamp}</div>
      <div className="flex items-start w-full select-none">
        {!!isPreview && (
          <div className="flex items-start relative ml-4 mr-4">
            <div className="absolute top-0 left-0 text-red-600 z-10 p-2">实时画面</div>
            <img
              src={`${address}:3000/video_stream?stream_id=${streamID.current}`}
              width={500}
              alt="预览"
            />
          </div>
        )}
        {data && (
          <div className="flex items-start select-none" key={data.timestamp}>
            <div className="ml-4 mr-4 relative">
              <div className="absolute top-0 left-0 text-red-600 z-10 p-2">RGB结果</div>
              <Image
                width={500}
                src={data.rgb_image}
                preview={{ maskClassName: "11", mask: <></> }}
              />
            </div>
            {(data as any).json_data && <PointCloudViewer data={(data as any).json_data} />}
          </div>
        )}
      </div>
    </>
  );
}

export default App;
