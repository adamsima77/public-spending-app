<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class NoticeLotIndexRequest extends FormRequest
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
            'procedure_id' => ['nullable', 'integer', 'exists:procedures,id'],
            'main_cpv' => ['nullable', 'string', 'exists:cpv_codes,code'],
            'nuts_code' => ['nullable', 'string', 'exists:nut_codes,code'],
            'eu_funded' => ['nullable', 'boolean'],
            'per_page' => ['nullable', 'integer', 'between:1,100'],
        ];
    }
}
