'use client';
import Style from './header.module.scss';
import Button from '@/components/button';
import Modal from '@/components/modal';
import useModal from '@/hooks/useModal';
import Settings from '@/components/settings';

export default function Header() {
  const { isOpen, open, close } = useModal();

  return (
    <>
      <header className={Style.Header}>
        <div>
          <h1 className={Style.Heading}>RealityFirst</h1>
        </div>
        <div>
          <Button text={'Настройки'} onClick={open} disabled={false} type={'primary'} />
        </div>
      </header>
      <Modal isOpen={isOpen} onClose={close} heading={'Настройки'}>
        <Settings />
      </Modal>
    </>
  );
}
