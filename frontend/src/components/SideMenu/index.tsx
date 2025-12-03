import { Space } from "antd";
import MenuIndicators from "../MenuIndicators";
import MenuModels from "../MenuModels";
import styles from './style.module.css';


export default function SideMenu() {
  return (
    <div
      className={styles.container}
    >
      <Space orientation="vertical">
        <MenuIndicators/>
        <MenuModels/>
      </Space>
    </div>
  )
}