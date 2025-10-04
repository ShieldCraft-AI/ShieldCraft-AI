import React, { useState, useRef, useEffect, useCallback } from 'react';
import PortalLayout from '../components/PortalLayout';
import DataLakeCard from '../components/dashboard/DataLakeCard';
import ApiLatencyCard from '../components/dashboard/ApiLatencyCard';
import ActiveUsersCard from '../components/dashboard/ActiveUsersCard';
import ThreatsCard from '../components/dashboard/ThreatsCard';
import ProcessingCard from '../components/dashboard/ProcessingCard';
import ResourceUsageCard from '../components/dashboard/ResourceUsageCard';
import styles from './dashboard.module.css';

// Define the card components mapping
const cardComponents = {
    'datalake': { component: DataLakeCard, title: 'Data Lake' },
    'api-latency': { component: ApiLatencyCard, title: 'API Latency' },
    'resources': { component: ResourceUsageCard, title: 'Resource Usage' },
    'active-users': { component: ActiveUsersCard, title: 'Active Users' },
    'threats': { component: ThreatsCard, title: 'Threats' },
    'processing': { component: ProcessingCard, title: 'Processing' },
};

type CardId = keyof typeof cardComponents;

interface DraggableCardProps {
    id: CardId;
    index: number;
    draggedIndex: number;
    hoveredIndex: number;
    onMouseDown: (e: React.MouseEvent, index: number) => void;
    onTouchStart: (e: React.TouchEvent, index: number) => void;
    children: React.ReactNode;
}

function DraggableCard({ id, index, draggedIndex, hoveredIndex, onMouseDown, onTouchStart, children }: DraggableCardProps) {
    const isBeingDragged = draggedIndex === index;
    const isAfterDraggedItem = draggedIndex !== -1 && draggedIndex < index && hoveredIndex >= index;
    const isBeforeDraggedItem = draggedIndex !== -1 && draggedIndex > index && hoveredIndex <= index;

    // Calculate transform for smooth repositioning
    let transform = '';
    if (draggedIndex !== -1 && !isBeingDragged) {
        if (isAfterDraggedItem) {
            transform = 'translateX(-100%)';
        } else if (isBeforeDraggedItem) {
            transform = 'translateX(100%)';
        }
    }

    return (
        <div
            className={`${styles.draggableCard} ${isBeingDragged ? styles.cardDragging : ''
                }`}
            style={{
                transform: isBeingDragged ? 'scale(1.05)' : transform,
                zIndex: isBeingDragged ? 1000 : 1,
                transition: isBeingDragged ? 'none' : 'transform 0.3s cubic-bezier(0.2, 0, 0.2, 1)',
            }}
            onMouseDown={(e) => onMouseDown(e, index)}
            onTouchStart={(e) => onTouchStart(e, index)}
            data-card-id={id}
            role="button"
            tabIndex={0}
            aria-label={`Drag to reorder ${cardComponents[id].title} card`}
        >
            {children}
        </div>
    );
}

const Dashboard = () => {
    const [cards, setCards] = useState<CardId[]>([
        'datalake',
        'api-latency',
        'resources',
        'active-users',
        'threats',
        'processing'
    ]);

    const [draggedIndex, setDraggedIndex] = useState(-1);
    const [hoveredIndex, setHoveredIndex] = useState(-1);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

    const containerRef = useRef<HTMLDivElement>(null);
    const draggedCardRef = useRef<HTMLDivElement>(null);
    const isDragging = useRef(false);

    // Calculate grid positions for smooth reordering
    const getCardPosition = useCallback((index: number) => {
        if (!containerRef.current) return { x: 0, y: 0 };

        const container = containerRef.current;
        const containerRect = container.getBoundingClientRect();
        const cards = container.children;

        if (index >= cards.length) return { x: 0, y: 0 };

        const card = cards[index] as HTMLElement;
        const cardRect = card.getBoundingClientRect();

        return {
            x: cardRect.left - containerRect.left,
            y: cardRect.top - containerRect.top
        };
    }, []);

    // Handle mouse drag start
    const handleMouseDown = useCallback((e: React.MouseEvent, index: number) => {
        if (e.button !== 0) return; // Only left mouse button

        e.preventDefault();
        isDragging.current = true;
        setDraggedIndex(index);

        const rect = e.currentTarget.getBoundingClientRect();
        setDragStart({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        });
        setDragOffset({ x: 0, y: 0 });

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }, []);

    // Handle touch drag start
    const handleTouchStart = useCallback((e: React.TouchEvent, index: number) => {
        e.preventDefault();
        isDragging.current = true;
        setDraggedIndex(index);

        const touch = e.touches[0];
        const rect = e.currentTarget.getBoundingClientRect();
        setDragStart({
            x: touch.clientX - rect.left,
            y: touch.clientY - rect.top
        });
        setDragOffset({ x: 0, y: 0 });

        document.addEventListener('touchmove', handleTouchMove);
        document.addEventListener('touchend', handleTouchEnd);
    }, []);

    // Handle mouse move during drag
    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (!isDragging.current || !containerRef.current) return;

        const containerRect = containerRef.current.getBoundingClientRect();
        const mouseX = e.clientX - containerRect.left;
        const mouseY = e.clientY - containerRect.top;

        setDragOffset({
            x: mouseX - dragStart.x,
            y: mouseY - dragStart.y
        });

        // Find which card we're hovering over
        const cardElements = containerRef.current.children;
        let newHoveredIndex = -1;

        for (let i = 0; i < cardElements.length; i++) {
            const card = cardElements[i] as HTMLElement;
            const rect = card.getBoundingClientRect();
            const cardCenterX = rect.left + rect.width / 2 - containerRect.left;
            const cardCenterY = rect.top + rect.height / 2 - containerRect.top;

            if (Math.abs(mouseX - cardCenterX) < rect.width / 2 &&
                Math.abs(mouseY - cardCenterY) < rect.height / 2) {
                newHoveredIndex = i;
                break;
            }
        }

        setHoveredIndex(newHoveredIndex);
    }, [dragStart]);

    // Handle touch move during drag
    const handleTouchMove = useCallback((e: TouchEvent) => {
        if (!isDragging.current || !containerRef.current) return;

        e.preventDefault();
        const touch = e.touches[0];
        const containerRect = containerRef.current.getBoundingClientRect();
        const touchX = touch.clientX - containerRect.left;
        const touchY = touch.clientY - containerRect.top;

        setDragOffset({
            x: touchX - dragStart.x,
            y: touchY - dragStart.y
        });

        // Find which card we're hovering over
        const cardElements = containerRef.current.children;
        let newHoveredIndex = -1;

        for (let i = 0; i < cardElements.length; i++) {
            const card = cardElements[i] as HTMLElement;
            const rect = card.getBoundingClientRect();
            const cardCenterX = rect.left + rect.width / 2 - containerRect.left;
            const cardCenterY = rect.top + rect.height / 2 - containerRect.top;

            if (Math.abs(touchX - cardCenterX) < rect.width / 2 &&
                Math.abs(touchY - cardCenterY) < rect.height / 2) {
                newHoveredIndex = i;
                break;
            }
        }

        setHoveredIndex(newHoveredIndex);
    }, [dragStart]);

    // Handle mouse up - end drag
    const handleMouseUp = useCallback(() => {
        if (!isDragging.current) return;

        isDragging.current = false;

        if (draggedIndex !== -1 && hoveredIndex !== -1 && draggedIndex !== hoveredIndex) {
            setCards(prevCards => {
                const newCards = [...prevCards];
                const [draggedCard] = newCards.splice(draggedIndex, 1);
                newCards.splice(hoveredIndex, 0, draggedCard);
                return newCards;
            });
        }

        setDraggedIndex(-1);
        setHoveredIndex(-1);
        setDragOffset({ x: 0, y: 0 });

        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }, [draggedIndex, hoveredIndex, handleMouseMove]);

    // Handle touch end - end drag
    const handleTouchEnd = useCallback(() => {
        if (!isDragging.current) return;

        isDragging.current = false;

        if (draggedIndex !== -1 && hoveredIndex !== -1 && draggedIndex !== hoveredIndex) {
            setCards(prevCards => {
                const newCards = [...prevCards];
                const [draggedCard] = newCards.splice(draggedIndex, 1);
                newCards.splice(hoveredIndex, 0, draggedCard);
                return newCards;
            });
        }

        setDraggedIndex(-1);
        setHoveredIndex(-1);
        setDragOffset({ x: 0, y: 0 });

        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
    }, [draggedIndex, hoveredIndex, handleTouchMove]);

    // Cleanup event listeners on unmount
    useEffect(() => {
        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('touchmove', handleTouchMove);
            document.removeEventListener('touchend', handleTouchEnd);
        };
    }, [handleMouseMove, handleMouseUp, handleTouchMove, handleTouchEnd]);

    return (
        <PortalLayout title="Dashboard" description="ShieldCraft AI Dashboard">
            <div className={styles.dashboardContainer}>
                <main className={styles.main} id="dashboard">
                    <div
                        ref={containerRef}
                        className={styles.gridContainer}
                        style={{ position: 'relative' }}
                    >
                        {cards.map((cardId, index) => {
                            const CardComponent = cardComponents[cardId].component;
                            return (
                                <DraggableCard
                                    key={cardId}
                                    id={cardId}
                                    index={index}
                                    draggedIndex={draggedIndex}
                                    hoveredIndex={hoveredIndex}
                                    onMouseDown={handleMouseDown}
                                    onTouchStart={handleTouchStart}
                                >
                                    <CardComponent />
                                </DraggableCard>
                            );
                        })}

                        {/* Floating dragged card */}
                        {draggedIndex !== -1 && (
                            <div
                                ref={draggedCardRef}
                                className={styles.floatingCard}
                                style={{
                                    position: 'absolute',
                                    left: dragOffset.x,
                                    top: dragOffset.y,
                                    transform: 'scale(1.05)',
                                    opacity: 0.9,
                                    pointerEvents: 'none',
                                    zIndex: 1001,
                                }}
                            >
                                {React.createElement(cardComponents[cards[draggedIndex]].component)}
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </PortalLayout>
    );
};

export default Dashboard;
