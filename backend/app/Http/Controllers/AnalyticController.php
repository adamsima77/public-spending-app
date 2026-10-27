<?php

declare(strict_types=1);

namespace App\Http\Controllers;

class AnalyticController extends Controller
{
    public function index(string $val)
    {
        return response()->json([
            'message' => 'AnalyticController index',
            'value' => $val,
        ]);
    }
}
