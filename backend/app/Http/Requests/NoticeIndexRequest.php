<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class NoticeIndexRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'search' => ['nullable', 'string', 'max:255'],
            'notice_type' => ['nullable', 'array', 'max:50'],
            'notice_type.*' => ['string', 'max:32'],
            'form_type' => ['nullable', 'array', 'max:50'],
            'form_type.*' => ['string', 'max:32'],
            'procedure_id' => ['nullable', 'integer', 'exists:procedures,id'],
            'is_latest' => ['nullable', 'boolean'],
            'published_from' => ['nullable', 'date_format:Y-m-d'],
            'published_to' => ['nullable', 'date_format:Y-m-d', 'after_or_equal:published_from'],
            'sort' => ['nullable', 'string', 'in:title,notice_id,notice_type,published_at,issue_date,created_at'],
            'direction' => ['nullable', 'string', 'in:asc,desc'],
            'per_page' => ['nullable', 'integer', 'between:1,100'],
            'page' => ['nullable', 'integer', 'min:1'],
        ];
    }

    protected function prepareForValidation(): void
    {
        foreach (['notice_type', 'form_type'] as $key) {
            $value = $this->input($key . '[]', $this->input($key));

            if (is_string($value) && $value !== '') {
                $value = array_values(array_filter(array_map('trim', explode(',', $value))));
            }

            if (is_array($value)) {
                $this->merge([$key => $value]);
            }
        }
    }
}
