<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ProcedureIndexRequest extends FormRequest
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
            'procedure_type' => ['nullable', 'string', 'max:32'],
            'buyer_id' => ['nullable', 'integer', 'exists:organizations,id'],
            'main_cpv' => ['nullable', 'string', 'exists:cpv_codes,code'],
            'nuts_code' => ['nullable', 'string', 'exists:nut_codes,code'],
            'per_page' => ['nullable', 'integer', 'between:1,100'],
            'page' => ['nullable', 'integer', 'min:1'],
        ];
    }
}
