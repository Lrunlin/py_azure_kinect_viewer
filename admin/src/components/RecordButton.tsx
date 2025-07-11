import React, { useEffect, useState, useRef } from "react";
import { Button, message, Spin } from "antd";
import { PoweroffOutlined, VideoCameraAddOutlined, VideoCameraOutlined } from "@ant-design/icons";

type RecordStatus = boolean; // true: 录制中，false: 未录制

const WS_URL = "ws://localhost:3000/ws/recording_status";

const RecordButton: React.FC<{ address: string }> = ({ address }) => {
  const [recording, setRecording] = useState<RecordStatus>(false);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const START_API = address + ":3000/start_record";
  const STOP_API = address + ":3000/stop_record";

  // 建立 WebSocket
  useEffect(() => {
    let ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onmessage = event => {
      try {
        const data = JSON.parse(event.data);
        if (typeof data.recording === "boolean") {
          setRecording(data.recording);
        }
      } catch {}
    };
    ws.onopen = () => {
      ws.send("get");
    };
    ws.onclose = () => {
      // 可尝试重连
      setTimeout(() => {
        wsRef.current = new WebSocket(WS_URL);
      }, 1000);
    };
    return () => {
      ws.close();
    };
  }, []);

  // 切换录制
  const handleClick = async () => {
    setLoading(true);
    try {
      const api = recording ? STOP_API : START_API;
      const resp = await fetch(api, { method: "POST" });
      const result = await resp.json();
      if (result.success) {
        message.success(result.msg);
        setRecording(val => !val);
        // 状态变化由WebSocket同步，不在这里setRecording
      } else {
        message.error(result.msg || "操作失败");
      }
    } catch (e) {
      message.error("请求失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        type="primary"
        danger={recording}
        icon={recording ? <VideoCameraOutlined /> : <VideoCameraAddOutlined />}
        loading={loading}
        onClick={handleClick}
        className="px-8 ml-4 py-2 rounded-xl text-lg shadow-lg"
        style={{
          backgroundColor: recording ? "#ff4d4f" : undefined,
          color: recording ? "#fff" : undefined,
          borderColor: recording ? "#ff4d4f" : undefined,
        }}
      >
        {recording ? "正在录制" : "未录制"}
      </Button>
    </>
  );
};

export default RecordButton;
