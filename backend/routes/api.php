<?php

use App\Http\Controllers\DownloadedFileController;
use App\Http\Controllers\EtlLogController;
use App\Http\Controllers\NoticeController;
use App\Http\Controllers\NoticeLotController;
use App\Http\Controllers\NutCodeController;
use App\Http\Controllers\OrganizationController;
use App\Http\Controllers\ProcedureController;
use App\Http\Controllers\SystemLogController;
use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;


Route::middleware(['auth:sanctum'])->prefix('downloaded-files')->group(function () {
    Route::get('/', [DownloadedFileController::class, 'index'] );
    Route::get('/{file}', [DownloadedFileController::class, 'show']);
});

Route::middleware(['auth:sanctum'])->prefix('etl-logs')->group(function () {
    Route::get('/', [EtlLogController::class, 'index']);
    Route::get('/{etlLog}', [EtlLogController::class, 'show']);
});

Route::prefix('notices')->group(function () {
    Route::get('/', [NoticeController::class, 'index']);
    Route::get('/{notice}', [NoticeController::class, 'show']);
});

Route::prefix('notice-lots')->group(function () {
    Route::get('/', [NoticeLotController::class, 'index']);
    Route::get('/{noticeLot}', [NoticeLotController::class, 'show']);
});

Route::middleware(['auth:sanctum'])->group(function () {
    Route::apiResource('nut-codes', NutCodeController::class)
        ->parameters(['nut-codes' => 'nutCode'])
        ->except(['index', 'show']);
});

Route::apiResource('nut-codes', NutCodeController::class)
    ->parameters(['nut-codes' => 'nutCode'])
    ->only(['index', 'show']);

Route::prefix('organizations')->group(function () {
    Route::get('/', [OrganizationController::class, 'index']);
    Route::get('/{organization}', [OrganizationController::class, 'show']);
});

Route::prefix('procedures')->group(function () {
    Route::get('/', [ProcedureController::class, 'index']);
    Route::get('/{procedure}', [ProcedureController::class, 'show']);
});

Route::middleware(['auth:sanctum'])->prefix('system-logs')->group(function () {
    Route::get('/', [SystemLogController::class, 'index']);
    Route::get('/{systemLog}', [SystemLogController::class, 'show']);
});

Route::prefix('users')->group(function () {
    Route::middleware(['auth:sanctum'])->group(function () {
        Route::get('/', [UserController::class, 'index']);
        Route::get('/{user}', [UserController::class, 'show']);
        Route::put('/{user}', [UserController::class, 'update']);
        Route::delete('/{user}', [UserController::class, 'anonymize']);
        Route::post('/', [UserController::class, 'invite']);
    });
});
