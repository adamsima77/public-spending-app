<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;

class AnalyticController extends Controller
{
    public function index(string $val): JsonResponse
    {
        return response()->json([
            'message' => 'AnalyticController index',
            'value' => $val,
        ]);
    }
}
