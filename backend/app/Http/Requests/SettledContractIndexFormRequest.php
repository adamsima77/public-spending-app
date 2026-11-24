<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class SettledContractIndexFormRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, ValidationRule|array<mixed>|string> */
    public function rules(): array
    {
        return [
            'search' => ['nullable', 'string', 'max:255'],
            'notice_id' => ['nullable', 'string', 'max:100'],
            'procedure_id' => ['nullable', 'integer', 'min:1'],
            'buyer_id' => ['nullable', 'integer', 'exists:organizations,id'],
            'conclusion_from' => ['nullable', 'date_format:Y-m-d'],
            'conclusion_to' => [
                'nullable',
                'date_format:Y-m-d',
                Rule::when($this->filled('conclusion_from'), ['after_or_equal:conclusion_from']),
            ],
            'has_url' => ['nullable', 'boolean'],
            'has_tenders' => ['nullable', 'boolean'],
            'only_current' => ['nullable', 'boolean'],
            'sort' => ['nullable', Rule::in(['id', 'conclusion_date', 'created_at', 'title', 'contract_number'])],
            'direction' => ['nullable', Rule::in(['asc', 'desc'])],
            'per_page' => ['nullable', 'integer', 'min:1', 'max:100'],
            'page' => ['nullable', 'integer', 'min:1'],
        ];
    }

    protected function prepareForValidation(): void
    {
        $normalized = [];

        foreach (['has_url', 'has_tenders', 'only_current'] as $key) {
            if ($this->has($key)) {
                $normalized[$key] = filter_var($this->input($key), FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
        }

        $this->merge($normalized);
    }
}
