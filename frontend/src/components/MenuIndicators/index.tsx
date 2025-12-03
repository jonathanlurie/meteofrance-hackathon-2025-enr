import { Menu, type MenuProps } from 'antd';
import styles from './style.module.css';
import { useAtom } from 'jotai';
import { indicatorAtom } from '../../store';


type MenuItem = Required<MenuProps>['items'][number];






export default function MenuIndicators() {
  const [indicator, setIndicator] = useAtom(indicatorAtom)

  const items: MenuItem[] = [
    {
      key: 'sub1',
      label: 'Indicateurs',
      // icon: <MailOutlined />,
      children: [
        { key: 'dju', label: 'DJU' },
        { key: 'delta-dju', label: 'Delta DJU' },
        { key: 'solaire', label: 'Solaire' },
        { key: 'delta-solaire', label: 'Delta Solaire' },
        { key: 'eolien', label: 'Éolien' },
        { key: 'delta-eolien', label: 'Delta Éolien' },
      ],
    }
  ];

  const onClick: MenuProps['onClick'] = (e) => {
    console.log('click ', e);
    setIndicator(e.key);
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
        selectedKeys={[indicator]}
        mode="inline"
        items={items}
      />
    </div>
  )
}