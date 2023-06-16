import React, { useEffect } from 'react';
import {
  autoUpdate,
  flip,
  FloatingFocusManager,
  FloatingPortal,
  offset,
  shift,
  useDismiss,
  useFloating,
  useInteractions,
  useRole,
} from '@floating-ui/react';
import { getWidthStyles } from '@uikit/Popover/Popover.utils';
import { useForwardRef } from '@uikit/hooks/useForwardRef';
import { ChildWithRef } from '@uikit/types/element.types';
import { PopoverOptions } from '@uikit/Popover/Popover.types';

export interface PopoverProps extends PopoverOptions {
  isOpen: boolean;
  onOpenChange: (_isOpen: boolean) => void;
  triggerRef: React.RefObject<HTMLElement>;
  children: ChildWithRef;
}
const Popover: React.FC<PopoverProps> = ({
  isOpen,
  onOpenChange,
  children,
  triggerRef,
  placement = 'bottom-start',
  offset: offsetValue = 10,
  dependencyWidth,
}) => {
  const { refs, floatingStyles, context } = useFloating({
    placement,
    open: isOpen,
    onOpenChange,
    middleware: [offset(offsetValue), flip(), shift({ padding: 8 })],
    whileElementsMounted: autoUpdate,
  });

  useEffect(() => {
    triggerRef.current && refs.setReference(triggerRef.current);
  }, [triggerRef, refs]);

  const dismiss = useDismiss(context);
  const role = useRole(context);

  const { getFloatingProps } = useInteractions([dismiss, role]);

  const popoverPanel = React.Children.only(children);
  const ref = useForwardRef(refs.setFloating, children.ref);
  const panelStyle = { ...(children.props.style ?? {}), ...floatingStyles };
  if (dependencyWidth) {
    Object.entries(getWidthStyles(dependencyWidth, triggerRef)).forEach(([cssProperty, value]) => {
      panelStyle[cssProperty] = value;
    });
  }

  return (
    <FloatingPortal>
      {isOpen && (
        <FloatingFocusManager context={context}>
          {React.cloneElement(popoverPanel, { ref, ...children.props, style: panelStyle, ...getFloatingProps() })}
        </FloatingFocusManager>
      )}
    </FloatingPortal>
  );
};
export default Popover;
