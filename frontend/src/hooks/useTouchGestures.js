/**
 * Custom hook for touch gestures
 * Supports: swipe, tap, long press
 * 
 * Usage:
 * const gestures = useTouchGestures({
 *   onSwipeLeft: () => console.log('Swiped left'),
 *   onSwipeRight: () => console.log('Swiped right'),
 *   onTap: () => console.log('Tapped')
 * })
 * 
 * <div {...gestures}>Content</div>
 */
import { useRef, useCallback } from 'react'

export function useTouchGestures({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onTap,
  onLongPress,
  swipeThreshold = 50,
  longPressDelay = 500
} = {}) {
  const touchStart = useRef({ x: 0, y: 0, time: 0 })
  const longPressTimer = useRef(null)

  const handleTouchStart = useCallback((e) => {
    const touch = e.touches[0]
    touchStart.current = {
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    }

    // Start long press timer
    if (onLongPress) {
      longPressTimer.current = setTimeout(() => {
        onLongPress(e)
      }, longPressDelay)
    }
  }, [onLongPress, longPressDelay])

  const handleTouchMove = useCallback(() => {
    // Cancel long press if finger moves
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
      longPressTimer.current = null
    }
  }, [])

  const handleTouchEnd = useCallback((e) => {
    // Clear long press timer
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
      longPressTimer.current = null
    }

    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - touchStart.current.x
    const deltaY = touch.clientY - touchStart.current.y
    const deltaTime = Date.now() - touchStart.current.time

    // Check for swipe
    const absX = Math.abs(deltaX)
    const absY = Math.abs(deltaY)

    if (absX > swipeThreshold || absY > swipeThreshold) {
      // Horizontal swipe
      if (absX > absY) {
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight(e)
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft(e)
        }
      }
      // Vertical swipe
      else {
        if (deltaY > 0 && onSwipeDown) {
          onSwipeDown(e)
        } else if (deltaY < 0 && onSwipeUp) {
          onSwipeUp(e)
        }
      }
    }
    // Check for tap (quick touch with minimal movement)
    else if (absX < 10 && absY < 10 && deltaTime < 300 && onTap) {
      onTap(e)
    }
  }, [onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, onTap, swipeThreshold])

  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd
  }
}

// Specific gesture hooks
export function useSwipe({ onSwipeLeft, onSwipeRight, threshold = 50 }) {
  return useTouchGestures({
    onSwipeLeft,
    onSwipeRight,
    swipeThreshold: threshold
  })
}

export function useTap(onTap) {
  return useTouchGestures({ onTap })
}

export function useLongPress(onLongPress, delay = 500) {
  return useTouchGestures({ onLongPress, longPressDelay: delay })
}
