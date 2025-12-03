import { useEffect, useRef, useState } from 'react'
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl, { type MapMouseEvent } from "maplibre-gl";
import { getStyle, setLayerOpacity } from "basemapkit";
import { Protocol } from "pmtiles";
import styles from './style.module.css';
import { Colormap, MultiChannelSeriesTiledLayer, ColormapDescriptionLibrary, type MultiChannelSeriesTiledLayerSpecification } from 'shadertiledlayer';
import { climatelayerPickingValueAtom, mlMapAtom } from '../../store';
import { getDefaultStore, useAtom } from 'jotai';

const lang = "fr";
const pmtiles = "https://fsn1.your-objectstorage.com/public-map-data/pmtiles/planet.pmtiles";
const sprite = "https://raw.githubusercontent.com/jonathanlurie/phosphor-mlgl-sprite/refs/heads/main/sprite/phosphor-diecut";
const glyphs = "https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf";



export default function MlMap() {
  const [, setMlMap] = useAtom(mlMapAtom)
  const mapDivRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapDivRef.current) {
      return;
    }

    maplibregl.addProtocol("pmtiles", new Protocol().tile);

    (async () => {

      let  style = getStyle("spectre-purple", {
        pmtiles,
        sprite,
        glyphs,
        lang,
        hidePOIs: true,
    
        globe: false,
        // terrain: {
        //   pmtiles: "https://fsn1.your-objectstorage.com/public-map-data/pmtiles/terrain-mapterhorn.pmtiles",
        //   encoding: "terrarium"
        // }
      });

      style = setLayerOpacity("water", 0.2, style);

      const map = new maplibregl.Map({
        container: mapDivRef.current as HTMLDivElement,
        hash: false,
        style: style,
        maxPitch: 85,
        center: [4.326, 46.487],
        zoom: 5
      });

      if (!map) return;
      await new Promise((resolve) => map.on("load", resolve));

      setMlMap(map);

      const tileUrlPrefix = "http://127.0.0.1:8083/";
      const seriesInfoUrl = `${tileUrlPrefix}index.json`;
      const seriesInfoResponse = await fetch(seriesInfoUrl);
      const seriesInfo = (await seriesInfoResponse.json()) as MultiChannelSeriesTiledLayerSpecification;

      const climateLayer = new MultiChannelSeriesTiledLayer("climate-layer", {
        datasetSpecification: seriesInfo,
        colormap: Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: -10 + 273, max: 30 + 273 }),
        colormapGradient: true,
        tileUrlPrefix,
      });

      map.addLayer(climateLayer, "water");

      const store = getDefaultStore();

      map.on("mousemove", async (e: MapMouseEvent) => {
        try {
          const pickingInfo = await climateLayer.pick(e.lngLat);
          if (pickingInfo) {
            store.set(climatelayerPickingValueAtom, pickingInfo);
          } else {
            store.set(climatelayerPickingValueAtom, null);
          }
        } catch (_err) {
          store.set(climatelayerPickingValueAtom, null);
        }
      });

    })()
  }, [setMlMap]);


  return (
    <div ref={mapDivRef} className={styles.mapContainer} />
  )
}

