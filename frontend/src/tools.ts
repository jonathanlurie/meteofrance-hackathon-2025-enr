import { getDefaultStore } from "jotai";
import { indicatorAtom, layerAtom, mlMapAtom, modelAtom, monthAtom, traccValueAtom } from "./store";
import { Colormap, ColormapDescriptionLibrary, MultiChannelSeriesTiledLayer, type MultiChannelSeriesTiledLayerSpecification } from "shadertiledlayer";


const colormaps = {
  "dju": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: 0, max: 600 }),
  "tas": Colormap.fromColormapDescription(ColormapDescriptionLibrary.turbo , { min: -10, max: 25 }),
}



export async function addLayer() {
  // model: string, indicator: string, month:string, 
  const store = getDefaultStore();
  const map = store.get(mlMapAtom);
  const month = store.get(monthAtom);
  const model = store.get(modelAtom);
  const indicator = store.get(indicatorAtom);
  const traccValue = store.get(traccValueAtom)

  console.log(">>>", map);

  try {
    map?.removeLayer("climate-layer");
  } catch(e) {
    console.log(e);
  }
  
  const tileUrlPrefix = `/tilesets/${model.toUpperCase()}/${indicator}_${month}/`;
  const seriesInfoUrl = `${tileUrlPrefix}index.json`;

  console.log(">>>>", seriesInfoUrl);
  
  const seriesInfoResponse = await fetch(seriesInfoUrl);
  const seriesInfo = (await seriesInfoResponse.json()) as MultiChannelSeriesTiledLayerSpecification;

  const climateLayer = new MultiChannelSeriesTiledLayer("climate-layer", {
    datasetSpecification: seriesInfo,
    colormap: colormaps[indicator as keyof typeof colormaps],
    colormapGradient: true,
    tileUrlPrefix,
  });

  console.log("traccValue", traccValue);
  
  climateLayer.setSeriesAxisValue(traccValue);

  store.set(layerAtom, climateLayer)

  map?.addLayer(climateLayer, "water");


  // const store = getDefaultStore();

  // map.on("mousemove", async (e: MapMouseEvent) => {
  //   try {
  //     const pickingInfo = await climateLayer.pick(e.lngLat);
  //     if (pickingInfo) {
  //       store.set(climatelayerPickingValueAtom, pickingInfo);
  //     } else {
  //       store.set(climatelayerPickingValueAtom, null);
  //     }
  //   } catch (_err) {
  //     store.set(climatelayerPickingValueAtom, null);
  //   }
  // });

}