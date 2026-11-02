<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('lot_results', function (Blueprint $table): void {
            $table->id();
            $table->string('notice_id', 250);
            $table->foreignId('notice_record_id')->constrained('notices')->restrictOnDelete();
            $table->string('lot_reference', 64);
            $table->foreignId('lot_id')->nullable()->constrained('notice_lots')->nullOnDelete();

            $table->string('award_outcome', 32)->nullable();
            $table->string('non_award_reason', 32)->nullable();
            $table->decimal('lowest_offer_value', 14, 2)->nullable();
            $table->char('lowest_offer_currency', 3)->nullable();
            $table->decimal('highest_offer_value', 14, 2)->nullable();
            $table->char('highest_offer_currency', 3)->nullable();

            $table->jsonb('tender_refs')->default('[]');
            $table->jsonb('contract_refs')->default('[]');
            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['notice_record_id', 'lot_reference']);
            $table->index(['notice_id', 'lot_reference']);
            $table->index('lot_id');
            $table->index('award_outcome');
        });

        Schema::create('lot_result_submission_stats', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('lot_result_id')->constrained('lot_results')->cascadeOnDelete();
            $table->string('category_code', 32);
            $table->unsignedInteger('count')->nullable();
            $table->timestamps();

            $table->unique(['lot_result_id', 'category_code']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('lot_result_submission_stats');
        Schema::dropIfExists('lot_results');
    }
};
