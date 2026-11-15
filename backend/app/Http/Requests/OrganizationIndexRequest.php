<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class OrganizationIndexRequest extends FormRequest
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

            'country' => ['nullable', 'array', 'max:50'],
            'country.*' => ['string', 'size:3'],

            'nuts_code' => ['nullable', 'string', 'max:10'],

            'company_size' => ['nullable', 'array'],
            'company_size.*' => ['string', 'exists:cl_company_sizes,code'],
            'without_company_size' => ['nullable', 'boolean'],

            'role' => ['nullable', 'array'],
            'role.*' => ['string', 'in:buyer,supplier,tender_organization,other'],

            'sort' => ['nullable', 'string', 'in:name,cin,town,country,company_size,created_at'],
            'direction' => ['nullable', 'string', 'in:asc,desc'],

            'per_page' => ['nullable', 'integer', 'between:1,100'],
            'page' => ['nullable', 'integer', 'min:1'],
        ];
    }

    protected function prepareForValidation(): void
    {
        foreach (['country', 'company_size', 'role'] as $key) {
            $value = $this->input($key);

            if (is_string($value) && $value !== '') {
                $this->merge([
                    $key => array_values(array_filter(array_map('trim', explode(',', $value)))),
                ]);
            }
        }
    }
}
