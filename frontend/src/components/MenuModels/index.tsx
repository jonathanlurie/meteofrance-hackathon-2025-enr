import { Menu, type MenuProps } from 'antd';
import styles from './style.module.css';
import { useAtom } from 'jotai';
import { modelAtom } from '../../store';

type MenuItem = Required<MenuProps>['items'][number];

export default function MenuModels() {
  const [model, setModel] = useAtom(modelAtom)

  const items: MenuItem[] = [
    {
      key: 'sub1',
      label: 'Modèles',
      children: [
        { key: 'cmcc', label: 'CMCC-CM2-SR5' },
        { key: 'ipsl', label: 'IPSL-CM6A-LR' },
      ],
    }
  ];

  const onClick: MenuProps['onClick'] = (e) => {
    console.log('click ', e);
    setModel(e.key);
  };
  
  return (
    <div
      className={styles.container}
    >
      <Menu
        theme="light"
        onClick={onClick}
        style={{ width: 256 }}
        defaultOpenKeys={['sub1']}
        selectedKeys={[model]}
        mode="inline"
        items={items}
      />
    </div>
  )
}