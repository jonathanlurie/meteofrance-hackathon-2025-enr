import { Space } from "antd";
import MenuIndicators from "../MenuIndicators";
import MenuModels from "../MenuModels";
import styles from './style.module.css';
import { useAtom } from "jotai";
import {legendAtom } from "../../store";


export default function SideMenu() {
  const [legend, ] = useAtom(legendAtom);




  return (
    <div
      className={styles.container}
    >
      <Space orientation="vertical">
        <MenuIndicators/>
        <MenuModels/>
        {
          legend ?
          <div className={styles.legendContainer}>
            <span>{`${legend.min} ${legend.unit}`}</span>
            <img className={styles.colormapImage} src={legend?.url} />
            <span>{`${legend.max} ${legend.unit}`}</span>
          </div>
          :
          null
        }

      </Space>
    </div>
  )
}