<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notice_lots', function (Blueprint $table) {
            $table->id();
            $table->text('lot_reference');
            $table->text('title')->nullable();
            $table->text('description')->nullable();
            $table->decimal('estimated_value', 14, 2)->nullable();
            $table->string('estimated_currency', 10)->nullable();
            $table->string('main_cpv', 10)->nullable();
            $table->string('nuts_code', 10)->nullable();
            $table->text('place_of_performance')->nullable();
            $table->text('award_criterion')->nullable();
            $table->timestamp('submission_deadline')->nullable();
            $table->text('document_url')->nullable();
            $table->text('detail_url')->nullable();

            $table->integer('duration_value')->nullable();
            $table->string('duration_unit', 16)->nullable();
            $table->decimal('framework_max_value', 14, 2)->nullable();
            $table->string('framework_max_currency', 10)->nullable();

            $table->boolean('eu_funded')->nullable();
            $table->boolean('eordering_allowed')->nullable();
            $table->boolean('epayment_allowed')->nullable();
            $table->string('einvoicing', 16)->nullable();
            $table->string('variants_allowed', 32)->nullable();
            $table->string('reserved_execution', 32)->nullable();
            $table->string('reserved_participation', 32)->nullable();

            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();
            $table->index('eu_funded');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notice_lots');
    }
};