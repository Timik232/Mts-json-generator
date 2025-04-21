'use client';
import Style from './panelMessage.module.scss';
import Line from '@/components/line';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import Button from '@/components/button';
import MessageClient from './messageClient';
import MessageSystem from './messageSystem';
import axios from 'axios';
import { v7 as uuidv7 } from 'uuid';
import classNames from 'classnames';
import { AnimatePresence, motion } from 'framer-motion';
import { chatUrl, clearUrl } from '@/const/env';

interface Props {
  setJson: (value: object | null) => void;
}

export default function PanelMessage({ setJson }: Props) {
  const [uuid] = useState(uuidv7());
  const containerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [value, setValue] = useState('');
  const [disabled, setDisabled] = useState(false);
  const [harvestedMessage, setHarvestedMessage] = useState<string[]>([
    'Я хочу сделать схему для rest api запроса',
    'Мне нужна схема для отправки сообщения в kafka',
  ]);
  const [message, setMessage] = useState<{ type: 'client' | 'system'; text: string }[]>([
    {
      type: 'system',
      text: 'Здравствуйте! Я - интеллектуальный помощник, предназначенный для генерации JSON-схем, которые служат для описания бизнес логики и процессов интеграции. Отправьте мне сообщение "Я хочу сделать схему для rest api запроса", и мы сможем приступить к работе!',
    },
  ]);

  const fetchMessage = async () => {
    setHarvestedMessage([]);
    setMessage((prev) => [...prev, { type: 'client', text: value }]);
    setDisabled(true);
    const data = value;
    setValue('');
    const response = await axios.post(chatUrl, {
      session_id: uuid,
      message: data,
    });
    console.log(response.data);
    setMessage((prev) => [...prev, { type: 'system', text: response.data.response }]);
    if (response.data.json_schema === '') setDisabled(false);
    else {
      setJson(response.data.json_schema);
      setDisabled(false);
    }
  };

  const fetchMessageHarvested = async (harvested: string) => {
    setHarvestedMessage([]);
    setMessage((prev) => [...prev, { type: 'client', text: harvested }]);
    setDisabled(true);
    setValue('');
    const response = await axios.post(chatUrl, {
      session_id: uuid,
      message: harvested,
    });
    console.log(response.data);
    setMessage((prev) => [...prev, { type: 'system', text: response.data.response }]);
    if (response.data.json_schema === '') setDisabled(false);
    else {
      setJson(response.data.json_schema);
      setDisabled(false);
    }
  };

  const clearMessage = async () => {
    setDisabled(true);
    setValue('');
    setMessage([
      {
        type: 'system',
        text: 'Здравствуйте! Я - интеллектуальный помощник, предназначенный для генерации JSON-схем, которые служат для описания бизнес логики и процессов интеграции. Отправьте мне сообщение "Я хочу сделать схему для rest api запроса", и мы сможем приступить к работе!',
      },
    ]);
    setHarvestedMessage(['Я хочу сделать схему для rest api запроса', 'Мне нужна схема для отправки сообщения в kafka']);
    await axios.post(clearUrl, {
      session_id: uuid,
    });
    setJson(null);
    setDisabled(false);
  };

  const autoResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.max(textareaRef.current.scrollHeight, 32)}px`;
    }
  };

  useEffect(() => {
    autoResize();
  }, [value, value]);

  useLayoutEffect(() => {
    if (containerRef.current) {
      if (message.length > 1) {
        containerRef.current.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior: 'smooth',
        });
      } else {
        containerRef.current.scrollTo({
          top: 0,
          behavior: 'smooth',
        });
      }
    }
  }, [message]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.7 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        type: 'spring',
        stiffness: 500,
        damping: 30,
      }}
      className={Style.PanelGate}>
      <h3>Чат</h3>
      <Line />
      <div ref={containerRef} className={Style.BlockMessage}>
        <AnimatePresence>
          {message.map((elem, index) =>
            elem.type === 'client' ? (
              <MessageClient key={'message_' + index} text={elem.text} />
            ) : (
              <MessageSystem key={'message_' + index} text={elem.text} />
            ),
          )}
        </AnimatePresence>
      </div>
      <Line />
      <div className={Style.BlockInput}>
        <AnimatePresence>
          {harvestedMessage.length > 0 && (
            <div className={Style.HarvestedMessage}>
              {harvestedMessage.map((msg, index) => (
                <motion.div
                  initial={{ opacity: 0, scale: 0.7 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0 }}
                  transition={{
                    type: 'spring',
                    stiffness: 300,
                    damping: 20,
                  }}
                  key={'harvested_message_' + index}>
                  <Button text={msg} onClick={() => fetchMessageHarvested(msg)} disabled={false} type={'default'} />
                </motion.div>
              ))}
            </div>
          )}
        </AnimatePresence>
        <div className={classNames(Style.TextArea, disabled && Style.PanelDisabled)}>
          <div>
            <textarea
              ref={textareaRef}
              value={value}
              disabled={disabled}
              onChange={(event) => setValue(event.target.value)}
              placeholder={'Введите сообщение...'}
            />
          </div>
          <div className={Style.Buttons}>
            <Button type="default" onClick={() => clearMessage()} disabled={disabled} text={'Очистить'} />
            <Button type="primary" onClick={() => fetchMessage()} disabled={disabled} text={'Отправить'} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
