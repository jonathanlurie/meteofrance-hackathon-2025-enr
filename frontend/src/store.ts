import { atom } from 'jotai';
import type maplibregl from "maplibre-gl";
import type { Colormap, MultiChannelSeriesTiledLayer } from 'shadertiledlayer';


export type Legend = {
  min: number,
  max: number,
  url: string,
  unit: string,
}

export const mlMapAtom = atom<maplibregl.Map | null>(null);

export const climatelayerPickingValueAtom = atom <{ value: number, unit: string | undefined } | null>(null);

export const indicatorAtom = atom<string>("dju")
export const modelAtom = atom<string>("cmcc")
export const monthAtom = atom<string>("01")
export const traccValueAtom = atom<number>(1.5)
export const layerAtom = atom<MultiChannelSeriesTiledLayer | null>(null)
export const colormapAtom = atom<Colormap|null>(null)
export const legendAtom = atom<Legend | null>(null);