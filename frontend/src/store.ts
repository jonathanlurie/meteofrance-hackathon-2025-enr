import { atom } from 'jotai';
import type maplibregl from "maplibre-gl";

export const mlMapAtom = atom<maplibregl.Map | null>(null);

export const climatelayerPickingValueAtom = atom <{ value: number, unit: string | undefined } | null>(null);

export const indicatorAtom = atom<string>("dju")
export const modelAtom = atom<string>("cmcc")
export const monthAtom = atom<number>(1)
