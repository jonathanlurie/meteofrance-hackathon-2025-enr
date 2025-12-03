import { getDefaultStore } from "jotai";
import { climatelayerPickingValueAtom, colormapAtom, indicatorAtom, layerAtom, legendAtom, mlMapAtom, modelAtom, monthAtom, traccValueAtom } from "./store";
import { Colormap, ColormapDescriptionLibrary, MultiChannelSeriesTiledLayer, type MultiChannelSeriesTiledLayerSpecification } from "shadertiledlayer";
import type { MapMouseEvent, Subscription } from "maplibre-gl";




const turboTas = structuredClone(ColormapDescriptionLibrary.turbo)
turboTas[1].push(0)

const colormaps = {
  "dju": Colormap.fromColormapDescription(turboTas , { min: 0, max: 600 }),
  "tas": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: -10, max: 30 }),
  "tasmin0": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: 0, max: 30 }),
  "rsds": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: 0, max: 300 }),
  "ws": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: 0, max: 8 }),
}


let eventSub: Subscription | undefined = undefined;


export async function addLayer() {
  // model: string, indicator: string, month:string, 
  const store = getDefaultStore();
  const map = store.get(mlMapAtom);
  const month = store.get(monthAtom);
  const model = store.get(modelAtom);
  const indicator = store.get(indicatorAtom);
  const traccValue = store.get(traccValueAtom)

  try {
    map?.removeLayer("climate-layer");
  } catch(e) {
    console.log(e);
  }
  
  const tileUrlPrefix = `/tilesets/${model.toUpperCase()}/${indicator}_${month}/`;
  const seriesInfoUrl = `${tileUrlPrefix}index.json`;  
  const seriesInfoResponse = await fetch(seriesInfoUrl);
  const seriesInfo = (await seriesInfoResponse.json()) as MultiChannelSeriesTiledLayerSpecification;
  const colormap = colormaps[indicator as keyof typeof colormaps];

  console.log(seriesInfo);
  

  colormap.createImageObjectURL()
  .then((url) => {
    store.set(legendAtom, {
      ...colormap.getRange(),
      url,
      unit: seriesInfo.pixelUnit ?? "",
    })
  })

  store.set(colormapAtom, colormap)

  const climateLayer = new MultiChannelSeriesTiledLayer("climate-layer", {
    datasetSpecification: seriesInfo,
    colormap: colormap,
    colormapGradient: true,
    tileUrlPrefix,
  });
  
  climateLayer.setSeriesAxisValue(traccValue);
  store.set(layerAtom, climateLayer)
  map?.addLayer(climateLayer, "water");

  if (eventSub) {
    eventSub.unsubscribe()
  }

  eventSub = map?.on("mousemove", async (e: MapMouseEvent) => {
    try {
      const pickingInfo = await climateLayer.pick(e.lngLat);
      if (pickingInfo) {
        console.log(pickingInfo);
        
        store.set(climatelayerPickingValueAtom, pickingInfo);
      } else {
        store.set(climatelayerPickingValueAtom, null);
      }
    } catch (_err) {
      store.set(climatelayerPickingValueAtom, null);
    }
  });

}