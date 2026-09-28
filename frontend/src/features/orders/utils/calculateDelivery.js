/**
 * Расчет стоимости доставки
 * @param {Object} params
 * @param {number} params.cartTotal - Сумма товаров в корзине
 * @param {'delivery' | 'pickup'} params.deliveryMethod - Способ получения
 * @param {Object|null} params.selectedCity - Выбранный объект города (содержит delivery_cost)
 * @param {Object|null} params.config - CommercialConfig (is_free_delivery_active, free_delivery_threshold)
 * @returns {{ deliveryCost: number, isFree: boolean, freeThresholdRemaining: number }}
 */
export const calculateDeliveryCost = ({
	cartTotal = 0,
	deliveryMethod = 'pickup',
	selectedCity = null,
	config = null,
}) => {
	// 1. При самовывозе доставка всегда бесплатная
	if (deliveryMethod === 'pickup') {
		return {
			deliveryCost: 0,
			isFree: true,
			freeThresholdRemaining: 0,
		}
	}

	const numericCartTotal = Number(cartTotal) || 0
	const threshold = Number(config?.free_delivery_threshold) || 1000
	const isFreeDeliveryActive = config?.is_free_delivery_active ?? true

	// 2. Проверяем, достигнут ли порог бесплатной доставки
	const isEligibleForFreeDelivery = isFreeDeliveryActive && numericCartTotal >= threshold

	if (isEligibleForFreeDelivery) {
		return {
			deliveryCost: 0,
			isFree: true,
			freeThresholdRemaining: 0,
		}
	}

	// 3. Вычисляем базовую стоимость доставки по выбранному городу
	const baseCityCost = Number(selectedCity?.delivery_cost) || 0
	const remainingForFree = Math.max(0, threshold - numericCartTotal)

	return {
		deliveryCost: baseCityCost,
		isFree: false,
		freeThresholdRemaining: remainingForFree,
	}
}
