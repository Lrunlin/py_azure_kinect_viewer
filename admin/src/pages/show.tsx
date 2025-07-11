import DepthViewer from "@/components/DepthViewer/_Viewer.tsx";
import { useState, useEffect, useRef } from "react";

const Show = () => {
  const [address, setAddress] = useState(localStorage.address || "http://127.0.0.1"); //接收缓存地址
  const streamID = useRef(Date.now().toString());

  return (
    <>
      <div className="flex items-start">
        <div className="w-1/2">
          <img src={`${address}:3000/video_stream?stream_id=${streamID.current}`} alt="预览" />
          <img className="w-full" src={`${address}:3000/plate_stream?stream_id=${streamID.current}`} alt="预览" />
        </div>
        <DepthViewer />
      </div>
    </>
  );
};
export default Show;
