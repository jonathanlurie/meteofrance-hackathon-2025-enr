import { useEffect, useRef, useState } from 'react'
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl, { type MapMouseEvent } from "maplibre-gl";
import { getStyle, setLayerOpacity, swapLayers } from "basemapkit";
import { Protocol } from "pmtiles";
import { InfoCircleOutlined, SearchOutlined } from '@ant-design/icons';
import './App.css'
import { Colormap, MultiChannelSeriesTiledLayer, ColormapDescriptionLibrary, type MultiChannelSeriesTiledLayerSpecification } from 'shadertiledlayer';

import { Button, Drawer } from 'antd';
import MlMap from './components/MlMap';
import { climatelayerPickingValueAtom } from './store';
import { useAtom } from 'jotai';
import TraccSlider from './components/TraccSlider';
import MonthSlider from './components/MonthSlider';
import MenuIndicators from './components/MenuIndicators';
import SideMenu from './components/SideMenu';
import InfoDrawerContent from './components/InfoDrawerContent';


function App() {
  // const [count, setCount] = useState(0);
  const mapDivRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [climatelayerPickingValue, ] = useAtom(climatelayerPickingValueAtom);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);

  useEffect(() => {
    if (!mapDivRef.current) {
      return;
    }

    


      maplibregl.addProtocol("pmtiles", new Protocol().tile);

      const lang = "en";
      const pmtiles = "https://fsn1.your-objectstorage.com/public-map-data/pmtiles/planet.pmtiles";
      const sprite = "https://raw.githubusercontent.com/jonathanlurie/phosphor-mlgl-sprite/refs/heads/main/sprite/phosphor-diecut";
      const glyphs = "https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf";

      let  style = getStyle("spectre-purple", {
        pmtiles,
        sprite,
        glyphs,
        lang,
        hidePOIs: true,
    
        // globe: false,
        // terrain: {
        //   pmtiles: "https://fsn1.your-objectstorage.com/public-map-data/pmtiles/terrain-mapterhorn.pmtiles",
        //   encoding: "terrarium"
        // }
      });

      style = setLayerOpacity("water", 0.2, style);

      mapRef.current = new maplibregl.Map({
        container: mapDivRef.current as HTMLDivElement,
        hash: true,
        style: style,
        maxPitch: 85,
      });

      (async () => {
        if (!mapRef.current) return;
        await new Promise((resolve) => mapRef.current!.on("load", resolve));

        const tileUrlPrefix = "http://127.0.0.1:8083/";
        const seriesInfoUrl = `${tileUrlPrefix}temperature_2m.json`;
        const seriesInfoResponse = await fetch(seriesInfoUrl);
        const seriesInfo = (await seriesInfoResponse.json()) as MultiChannelSeriesTiledLayerSpecification;

        const climateLayer = new MultiChannelSeriesTiledLayer("climate-layer", {
          datasetSpecification: seriesInfo,
          colormap: Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: -25, max: 40, reverse: false }),
          colormapGradient: true,
          tileUrlPrefix,
        });

        mapRef.current.addLayer(climateLayer, "water");
      })()
  }, []);


  const buttonClick = () => {
    console.log("hello", mapRef.current);
    
  }

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
      <div className='element-container'>
        
        <span>{climatelayerPickingValue ? climatelayerPickingValue.value.toFixed(2) : ""}</span>
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
