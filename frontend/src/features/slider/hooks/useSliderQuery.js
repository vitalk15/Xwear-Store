import { useSuspenseQuery } from '@tanstack/react-query'
import { fetchSliderData } from '../api/sliderApi'

export const useSliderQuery = () => {
	return useSuspenseQuery({
		queryKey: ['slider'],
		queryFn: fetchSliderData,
		// Данные слайдера обновляются редко, поэтому кэшируем на 5 мин
		staleTime: 5 * 60 * 1000,
	})
}
