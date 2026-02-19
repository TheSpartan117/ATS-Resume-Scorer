import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should debounce callback execution', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebounce(callback, 500));

    // Call debounced function multiple times
    act(() => {
      result.current('test1');
      result.current('test2');
      result.current('test3');
    });

    // Callback should not be called yet
    expect(callback).not.toHaveBeenCalled();

    // Fast-forward time
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Callback should be called once with last argument
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith('test3');
  });

  it('should clear timeout on component unmount', () => {
    const callback = vi.fn();
    const { result, unmount } = renderHook(() => useDebounce(callback, 500));

    act(() => {
      result.current('test');
    });

    // Unmount before timeout completes
    unmount();

    // Fast-forward time
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Callback should not be called after unmount
    expect(callback).not.toHaveBeenCalled();
  });

  it('should update callback without resetting timer', () => {
    let callback = vi.fn(() => 'first');
    const { result, rerender } = renderHook(
      ({ cb }) => useDebounce(cb, 500),
      { initialProps: { cb: callback } }
    );

    // Call debounced function
    act(() => {
      result.current();
    });

    // Update callback
    const newCallback = vi.fn(() => 'second');
    rerender({ cb: newCallback });

    // Fast-forward time
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // New callback should be called (not old one)
    expect(callback).not.toHaveBeenCalled();
    expect(newCallback).toHaveBeenCalledTimes(1);
  });

  it('should handle multiple arguments', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebounce(callback, 500));

    act(() => {
      result.current('arg1', 'arg2', 'arg3');
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(callback).toHaveBeenCalledWith('arg1', 'arg2', 'arg3');
  });

  it('should reset timer on subsequent calls', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebounce(callback, 500));

    act(() => {
      result.current('first');
    });

    // Advance time partially
    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Call again before timeout
    act(() => {
      result.current('second');
    });

    // Advance time again
    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Should not have been called yet (timer reset)
    expect(callback).not.toHaveBeenCalled();

    // Complete the timer
    act(() => {
      vi.advanceTimersByTime(200);
    });

    // Should be called with second value
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith('second');
  });
});
