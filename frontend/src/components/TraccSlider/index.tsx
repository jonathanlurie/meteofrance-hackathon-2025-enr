import { useEffect, useRef, useState } from 'react';
import { Slider, type SliderSingleProps } from 'antd';
import styles from './style.module.css';
import { getDefaultStore, useAtom } from 'jotai';
import { layerAtom, traccValueAtom } from '../../store';

const marks: SliderSingleProps['marks'] = {
  1.5: '+1.5°C',
  2: '+2°C',
  2.7: '+2.7°C',
  4: {
    style: {
      color: '#f50',
    },
    label: <strong>+4°C</strong>,
  },
};


export default function TraccSlider() {
  const [traccValue, setTraccValue] = useAtom(traccValueAtom);

  const onChange = (e) => {
    const store = getDefaultStore();
    const layer = store.get(layerAtom);
    setTraccValue(e)

    if (!layer) {
      return;
    }
    
    layer.setSeriesAxisValue(e)
    
  }

  return (
    <div
      className={styles.traccSliderContainer}
    >
       <Slider  min={1.5} max={4} step={0.01} marks={marks} defaultValue={1.5} onChange={onChange}/>
    </div>
  )
}