import { useState } from "react";
import type { FC } from "react";
import { Button, Modal } from "antd";
import type { ButtonProps } from "antd";
import Viewer from "./Viewer.tsx";

const PointCloudViewer: FC<{ bottonProps: ButtonProps & { className?: string } }> = props => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOk = () => {
    setIsModalOpen(false);
  };
  return (
    <>
      <Button type="primary" onClick={() => setIsModalOpen(true)} {...props.bottonProps}>
        查看点云
      </Button>
      <Modal
        title="深度图预览"
        open={isModalOpen}
        style={{
          top: 50,
        }}
        destroyOnClose
        width={"calc(70vw + 48px)"}
        onCancel={handleOk}
        footer={[
          <Button key="ok" type="primary" onClick={handleOk}>
            关闭
          </Button>,
        ]}
      >
        <Viewer />
      </Modal>
    </>
  );
};
export default PointCloudViewer;
