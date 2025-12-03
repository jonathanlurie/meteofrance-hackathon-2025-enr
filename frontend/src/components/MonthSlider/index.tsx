import { useEffect, useRef, useState } from 'react';
import { Slider, type SliderSingleProps } from 'antd';
import styles from './style.module.css';
import { monthAtom } from '../../store';
import { useAtom } from 'jotai';
import { addLayer } from '../../tools';

const marks: SliderSingleProps['marks'] = {
  1: 'Janvier',
  2: 'Février',
  3: 'Mars',
  4: 'Avril',
  5: 'Mai',
  6: 'Juin',
  7: 'Juillet',
  8: 'Août',
  9: 'Septembre',
  10: 'Octobre',
  11: 'Novembre',
  12: 'Décembre',
};


export default function MonthSlider() {
  const [, setMonth] = useAtom(monthAtom);


  const changeMonth = (e) => {
    console.log(e);
    setMonth(e < 10 ? `0${e}`: e.toString());
    addLayer()
  }

  return (
    <div
      className={styles.monthSliderContainer}
    >
       <Slider  min={1} max={12} step={1} marks={marks} defaultValue={1} onChange={changeMonth}/>
    </div>
  )
}