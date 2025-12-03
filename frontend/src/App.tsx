import { useEffect, useRef, useState } from 'react'
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { getStyle, setLayerOpacity } from "basemapkit";
import { Protocol } from "pmtiles";
import { InfoCircleOutlined } from '@ant-design/icons';
import './App.css'
import { Colormap, MultiChannelSeriesTiledLayer, ColormapDescriptionLibrary, type MultiChannelSeriesTiledLayerSpecification } from 'shadertiledlayer';

import { Button, Drawer } from 'antd';
import MlMap from './components/MlMap';
import { climatelayerPickingValueAtom } from './store';
import { useAtom } from 'jotai';
import TraccSlider from './components/TraccSlider';
import MonthSlider from './components/MonthSlider';
import SideMenu from './components/SideMenu';
import InfoDrawerContent from './components/InfoDrawerContent';


function App() {
  const [climatelayerPickingValue, ] = useAtom(climatelayerPickingValueAtom);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);

  const onOpenDrawer = () => {
    setDrawerOpen(true);
  }

  const onCloseDrawer = () => {
    setDrawerOpen(false);
  }

  return (
    <>
      <Button className="infoButton" icon={<InfoCircleOutlined />} onClick={onOpenDrawer}>Info</Button>
      <TraccSlider/>
      <MonthSlider/>
      <SideMenu/>
      
      <a
        href="https://www.data.gouv.fr/reuses/climate4energie/"
        target="_blank"
        rel="noopener noreferrer"
        className="mf-logo-link"
      >
        <img className='mf-logo' src="/logo-meteo-france.svg" alt="Meteo France Logo" />
      </a>
      <div className='element-container'>
        
        <span>{climatelayerPickingValue ? `${climatelayerPickingValue.value.toFixed(2)} ${climatelayerPickingValue.unit}` : ""}</span>
      </div>
      <MlMap />
      <Drawer
        title="Drawer blur"
        placement="right"
        mask={false}
        onClose={onCloseDrawer}
        open={drawerOpen}
      >
        <InfoDrawerContent/>
      </Drawer>
    </>
  )
}

export default App
