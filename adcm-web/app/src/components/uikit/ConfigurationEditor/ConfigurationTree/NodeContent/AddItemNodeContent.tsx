import { useRef } from 'react';
import { Icon } from '@uikit';
import { ConfigurationNode } from '../../ConfigurationEditor.types';
import s from '../ConfigurationTree.module.scss';
import cn from 'classnames';

export interface AddItemNodeContentProps {
  node: ConfigurationNode;
  onClick: (node: ConfigurationNode, nodeRef: React.RefObject<HTMLElement>) => void;
}

const AddItemNodeContent = ({ node, onClick }: AddItemNodeContentProps) => {
  const ref = useRef(null);

  const handleClick = () => {
    onClick(node, ref);
  };

  return (
    <div ref={ref} className={cn(s.nodeContent, s.addArrayItemNodeContent)} onClick={handleClick}>
      <Icon name="g1-add" size={16} /> {node.data.title}
    </div>
  );
};

export default AddItemNodeContent;