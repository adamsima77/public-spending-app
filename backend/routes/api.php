<?php

declare(strict_types=1);

use App\Http\Controllers\CpvCodeController;
use App\Http\Controllers\DownloadedFileController;
use App\Http\Controllers\EtlLogController;
use App\Http\Controllers\FilterController;
use App\Http\Controllers\NoticeController;
use App\Http\Controllers\NoticeLotController;
use App\Http\Controllers\NutCodeController;
use App\Http\Controllers\OrganizationController;
use App\Http\Controllers\ProcedureController;
use App\Http\Controllers\SystemLogController;
use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

Route::middleware('throttle:public-api')->group(function (): void {
    Route::prefix('codelists')->name('codelists.')->group(function (): void {
        Route::get('applicabilities', [FilterController::class, 'applicabilities'])->name('applicabilities');
        Route::get('award-criterion-types', [FilterController::class, 'awardCriterionTypes'])->name('award-criterion-types');
        Route::get('award-outcomes', [FilterController::class, 'awardOutcomes'])->name('award-outcomes');
        Route::get('company-sizes', [FilterController::class, 'companySizes'])->name('company-sizes');
        Route::get('contract-natures', [FilterController::class, 'contractNatures'])->name('contract-natures');
        Route::get('duration-units', [FilterController::class, 'durationUnits'])->name('duration-units');
        Route::get('form-types', [FilterController::class, 'formTypes'])->name('form-types');
        Route::get('legal-bases', [FilterController::class, 'legalBases'])->name('legal-bases');
        Route::get('non-award-reasons', [FilterController::class, 'nonAwardReasons'])->name('non-award-reasons');
        Route::get('notice-types', [FilterController::class, 'noticeTypes'])->name('notice-types');
        Route::get('permissions', [FilterController::class, 'permissions'])->name('permissions');
        Route::get('procedure-types', [FilterController::class, 'procedureTypes'])->name('procedure-types');
        Route::get('reserved-procurement', [FilterController::class, 'reservedProcurement'])->name('reserved-procurement');
        Route::get('submission-types', [FilterController::class, 'submissionTypes'])->name('submission-types');
    });
    Route::apiResource('notices', NoticeController::class)->only(['index', 'show']);
    Route::apiResource('notice-lots', NoticeLotController::class)
        ->parameters(['notice-lots' => 'noticeLot'])
        ->only(['index', 'show']);
    Route::apiResource('organizations', OrganizationController::class)->only(['index', 'show']);
    Route::apiResource('procedures', ProcedureController::class)->only(['index', 'show']);
    Route::apiResource('nut-codes', NutCodeController::class)
        ->parameters(['nut-codes' => 'nutCode'])
        ->only(['index', 'show']);
    Route::apiResource('cpv-codes', CpvCodeController::class)
        ->parameters(['cpv-codes' => 'cpvCode'])
        ->only(['index', 'show']);
});

Route::middleware(['auth:sanctum', 'throttle:admin-api'])->group(function (): void {
    Route::apiResource('downloaded-files', DownloadedFileController::class)
        ->parameters(['downloaded-files' => 'downloadedFile'])
        ->only(['index', 'show']);
    Route::apiResource('etl-logs', EtlLogController::class)
        ->parameters(['etl-logs' => 'etlLog'])
        ->only(['index', 'show']);
    Route::apiResource('system-logs', SystemLogController::class)
        ->parameters(['system-logs' => 'systemLog'])
        ->only(['index', 'show']);
});

Route::prefix('users')->group(function (): void {
    Route::middleware(['auth:sanctum', 'throttle:admin-api'])->group(function (): void {
        Route::get('/', [UserController::class, 'index']);
        Route::get('/{user}', [UserController::class, 'show']);
        Route::put('/{user}', [UserController::class, 'update']);
        Route::delete('/{user}', [UserController::class, 'anonymize']);
        Route::post('/', [UserController::class, 'invite']);
    });
});
