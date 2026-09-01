# Relatório de Acionamento PLEM/PRAI — HtmlViewer

Substitui a tela de "Detalhes" (form de campos) por um relatório único.

## Parte 1 — montar as coleções (OnVisible da tela ou OnSelect do botão "Relatório")

Formato **barra de fórmulas pt-BR** (`;` entre argumentos, `;;` entre comandos).

```powerfx
// ===== 1) Atividades do acionamento com a hora convertida em data/hora real =====
// A coluna Hora é TEXTO no formato "dd/mm/aaaa hh:mm[:ss]"; DateTimeValue depende
// do idioma do usuário, então a conversão é feita por posição (à prova de locale).
ClearCollect(
    colRelBase;
    ForAll(
        Filter(
            tbl_atividadesPlemPrai;
            ID_acionamento = var_dadosAcionamento.ID;
            Excluido <> true
        ) As _a;
        {
            Id: _a.ID;
            Acao: Upper(Coalesce(_a.Acao; "REGISTRO"));
            Texto: Coalesce(_a.Atividade; "");
            IdEntidade: Coalesce(_a.ID_entidade; 0);
            IdEquip: Coalesce(_a.ID_equipamento; 0);
            Situacao: Coalesce(_a.Status; "");
            Momento: If(
                Len(_a.Hora) >= 16;
                DateTime(
                    Value(Mid(_a.Hora; 7; 4));
                    Value(Mid(_a.Hora; 4; 2));
                    Value(Mid(_a.Hora; 1; 2));
                    Value(Mid(_a.Hora; 12; 2));
                    Value(Mid(_a.Hora; 15; 2));
                    0
                )
            )
        }
    )
);;

// ===== 2) Resolve ator (entidade ou equipamento) e prazo de chegada, e ordena =====
ClearCollect(
    colRelOrd;
    SortByColumns(
        ForAll(
            colRelBase As _b;
            {
                Id: _b.Id;
                Acao: _b.Acao;
                Texto: _b.Texto;
                IdEntidade: _b.IdEntidade;
                Situacao: _b.Situacao;
                Momento: _b.Momento;
                Ator: Coalesce(
                    LookUp(tbl_equipamentosAcionamentos; ID = _b.IdEquip).Item;
                    LookUp(tbl_FluxogramaAcionamentos; ID = _b.IdEntidade).Titulo;
                    ""
                );
                Nivel: Coalesce(LookUp(tbl_FluxogramaAcionamentos; ID = _b.IdEntidade).Nivel.Value; "");
                Prazo: Coalesce(
                    LookUp(tbl_equipamentosAcionamentos; ID = _b.IdEquip).Prazo_de_chegada_em_minutos;
                    LookUp(tbl_FluxogramaAcionamentos; ID = _b.IdEntidade).Prazo_de_chegada_em_minutos;
                    0
                )
            }
        );
        "Momento"; SortOrder.Ascending;
        "Id"; SortOrder.Ascending
    )
);;

// ===== 3) Marco zero do relatório =====
Set(
    varRelT0;
    Coalesce(var_dadosAcionamento.Data; First(colRelOrd).Momento)
);;

// ===== 4) Timeline com os três tempos: desde a abertura, desde o item anterior
//        e tempo de resposta (gatilho do próprio ator -> retorno dele) =====
ClearCollect(
    colRelTimeline;
    ForAll(
        Sequence(CountRows(colRelOrd)) As _i;
        With(
            {
                _r: Last(FirstN(colRelOrd; _i.Value));
                _ant: Last(FirstN(colRelOrd; Max(_i.Value - 1; 1)))
            };
            With(
                {
                    _gatilho: Last(
                        Filter(
                            FirstN(colRelOrd; _i.Value - 1);
                            IdEntidade = _r.IdEntidade;
                            IdEntidade > 0;
                            Acao in ["ACIONAR"; "ACIONAR_SOBREAVISO"; "SOBREAVISO"; "INFORMAR"; "NOTIFICADO"]
                        )
                    )
                };
                {
                    Ordem: _i.Value;
                    Id: _r.Id;
                    Acao: _r.Acao;
                    Texto: _r.Texto;
                    Ator: _r.Ator;
                    Nivel: _r.Nivel;
                    Prazo: _r.Prazo;
                    Situacao: _r.Situacao;
                    Momento: _r.Momento;
                    SegAbertura: DateDiff(varRelT0; _r.Momento; TimeUnit.Seconds);
                    SegAnterior: If(_i.Value = 1; 0; DateDiff(_ant.Momento; _r.Momento; TimeUnit.Seconds));
                    GatilhoMomento: _gatilho.Momento;
                    SegResposta: If(
                        _r.Acao in ["CHEGOU"; "RESPONDEU AO FLOW"; "NAO COMPARECERA"; "CONTATO_NR"; "SEM RESPOSTA"]
                            And !IsBlank(_gatilho.Momento);
                        DateDiff(_gatilho.Momento; _r.Momento; TimeUnit.Seconds)
                    )
                }
            )
        )
    )
)
```

## Parte 2 — HtmlText do controle HtmlViewer

Propriedades do controle: `AutoHeight = true`, `Font = Font.'Open Sans'`, `Size = 10`,
`Fill = RGBA(0,0,0,0)`, `Width = Parent.Width`, dentro de um container com
`LayoutOverflowY = LayoutOverflow.Scroll`.

```powerfx
=With(
    {
        _ac: var_dadosAcionamento;
        _tl: colRelTimeline
    };
    With(
        {
            _resp: Filter(_tl; !IsBlank(SegResposta); Acao in ["CHEGOU"; "RESPONDEU AO FLOW"]);
            _acion: Filter(_tl; Acao in ["ACIONAR"; "ACIONAR_SOBREAVISO"; "SOBREAVISO"; "INFORMAR"]);
            _fim: Coalesce(_ac.Data_termino; Now());
            _fnt: "font-family:'Segoe UI',Arial,sans-serif;";
            _lbl: "font-size:9px;letter-spacing:.13em;font-weight:700;color:#5D6B77;";
            _val: "font-size:13px;font-weight:600;color:#22303B;margin-top:3px;";
            _tdc: "padding:9px 16px 9px 0;vertical-align:top;width:33%;";
            _sec: "background:#FFFFFF;border:1px solid #E1E7EC;border-top:3px solid #155E8F;padding:14px 16px;margin-top:12px;";
            _hsec: "font-size:11px;font-weight:800;letter-spacing:.16em;color:#0B2E4F;border-bottom:1px solid #EDF1F4;padding-bottom:8px;margin-bottom:2px;";
            _kpi: "padding:12px 14px;border-right:1px solid #E1E7EC;vertical-align:top;"
        };
        With(
            {
                _mSeg: If(CountRows(_resp) > 0; Round(Average(_resp; SegResposta); 0); Blank());
                _pSeg: If(CountRows(_resp) > 0; Min(_resp; SegResposta); Blank());
                _xSeg: If(CountRows(_resp) > 0; Max(_resp; SegResposta); Blank());
                _totMin: DateDiff(Coalesce(_ac.Data; varRelT0); _fim; TimeUnit.Minutes);
                _semRetorno: Max(CountRows(_acion) - CountRows(_resp); 0);
                _corStatus: If(
                    _ac.Status = "Finalizado"; "#1F7A4D";
                    _ac.Status = "Em andamento"; "#B98900";
                    "#5D6B77"
                );
                _corAmb: If(_ac.Ambiente = "Ambiente Simulado"; "#C05621"; "#A62639")
            };
            With(
                {
                    _mTxt: If(
                        IsBlank(_mSeg); "—";
                        _mSeg < 60; Text(_mSeg) & "s";
                        _mSeg < 3600; Text(RoundDown(_mSeg / 60; 0)) & "m " & Text(Mod(_mSeg; 60)) & "s";
                        Text(RoundDown(_mSeg / 3600; 0)) & "h " & Text(RoundDown(Mod(_mSeg; 3600) / 60; 0)) & "m"
                    );
                    _pTxt: If(
                        IsBlank(_pSeg); "—";
                        _pSeg < 60; Text(_pSeg) & "s";
                        _pSeg < 3600; Text(RoundDown(_pSeg / 60; 0)) & "m " & Text(Mod(_pSeg; 60)) & "s";
                        Text(RoundDown(_pSeg / 3600; 0)) & "h " & Text(RoundDown(Mod(_pSeg; 3600) / 60; 0)) & "m"
                    );
                    _xTxt: If(
                        IsBlank(_xSeg); "—";
                        _xSeg < 60; Text(_xSeg) & "s";
                        _xSeg < 3600; Text(RoundDown(_xSeg / 60; 0)) & "m " & Text(Mod(_xSeg; 60)) & "s";
                        Text(RoundDown(_xSeg / 3600; 0)) & "h " & Text(RoundDown(Mod(_xSeg; 3600) / 60; 0)) & "m"
                    );
                    _durTxt: If(
                        _totMin < 60; Text(_totMin) & " min";
                        Text(RoundDown(_totMin / 60; 0)) & "h " & Text(Mod(_totMin; 60)) & "min"
                    )
                };

                "<div style='" & _fnt & "color:#22303B;font-size:12px;line-height:1.45;background:#F5F7F9;padding:0 0 14px 0;'>" &

                /* ============ CABEÇALHO ============ */
                "<div style='background:#0B2E4F;padding:16px 18px;'>" &
                    "<table cellspacing='0' cellpadding='0' style='width:100%;'><tr>" &
                        "<td style='vertical-align:top;'>" &
                            "<div style='font-size:9px;letter-spacing:.20em;font-weight:700;color:#7FA6C4;'>RELATÓRIO DE ACIONAMENTO &nbsp;&middot;&nbsp; " & Upper(Coalesce(_ac.Acionamento; "PLEM")) & "</div>" &
                            "<div style='font-size:21px;font-weight:800;color:#FFFFFF;margin-top:4px;letter-spacing:.01em;'>" & Coalesce(_ac.Protocolo; "SEM PROTOCOLO") & "</div>" &
                            "<div style='font-size:12px;color:#C7D8E5;margin-top:3px;'>" & Coalesce(_ac.Aeroporto; "—") & " &nbsp;&middot;&nbsp; " & Coalesce(_ac.IATA; "—") & " &nbsp;&middot;&nbsp; BLOCO " & Upper(Coalesce(_ac.Bloco; "—")) & "</div>" &
                        "</td>" &
                        "<td style='vertical-align:top;text-align:right;white-space:nowrap;'>" &
                            "<span style='display:inline-block;padding:3px 10px;background:" & _corStatus & ";color:#FFFFFF;font-size:10px;font-weight:700;letter-spacing:.08em;border-radius:10px;'>" & Upper(Coalesce(_ac.Status; "—")) & "</span>" &
                            "&nbsp;<span style='display:inline-block;padding:3px 10px;background:" & _corAmb & ";color:#FFFFFF;font-size:10px;font-weight:700;letter-spacing:.08em;border-radius:10px;'>" & Upper(Coalesce(_ac.Ambiente; "—")) & "</span>" &
                            "<div style='font-size:11px;color:#C7D8E5;margin-top:8px;'>registro " & _ac.ID & "</div>" &
                        "</td>" &
                    "</tr></table>" &
                    "<div style='margin-top:12px;background:#12456F;border-left:3px solid #4FA3E3;padding:8px 12px;'>" &
                        "<span style='font-size:9px;letter-spacing:.14em;color:#9FC4DE;font-weight:700;'>EMERGÊNCIA</span>" &
                        "<div style='font-size:14px;font-weight:700;color:#FFFFFF;margin-top:2px;'>" & Coalesce(_ac.Emergencia; "—") & "</div>" &
                    "</div>" &
                "</div>" &

                /* ============ FAIXA DE INDICADORES ============ */
                "<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;background:#FFFFFF;border:1px solid #E1E7EC;border-top:0;'><tr>" &
                    "<td style='" & _kpi & "'><div style='" & _lbl & "'>DURAÇÃO</div><div style='font-size:16px;font-weight:800;color:#0B2E4F;margin-top:3px;'>" & _durTxt & "</div><div style='font-size:10px;color:#8A98A4;'>" & If(IsBlank(_ac.Data_termino); "em andamento"; "encerrado") & "</div></td>" &
                    "<td style='" & _kpi & "'><div style='" & _lbl & "'>ATIVIDADES</div><div style='font-size:16px;font-weight:800;color:#0B2E4F;margin-top:3px;'>" & CountRows(_tl) & "</div><div style='font-size:10px;color:#8A98A4;'>registros na linha do tempo</div></td>" &
                    "<td style='" & _kpi & "'><div style='" & _lbl & "'>ACIONADOS</div><div style='font-size:16px;font-weight:800;color:#0B2E4F;margin-top:3px;'>" & CountRows(_acion) & "</div><div style='font-size:10px;color:#8A98A4;'>" & _semRetorno & " sem retorno</div></td>" &
                    "<td style='" & _kpi & "'><div style='" & _lbl & "'>TEMPO MÉDIO</div><div style='font-size:16px;font-weight:800;color:#1F7A4D;margin-top:3px;'>" & _mTxt & "</div><div style='font-size:10px;color:#8A98A4;'>resposta dos acionados</div></td>" &
                    "<td style='padding:12px 14px;vertical-align:top;'><div style='" & _lbl & "'>MENOR / MAIOR</div><div style='font-size:16px;font-weight:800;color:#0B2E4F;margin-top:3px;'>" & _pTxt & " <span style='color:#C9D3DB;'>/</span> " & _xTxt & "</div><div style='font-size:10px;color:#8A98A4;'>1ª e última resposta</div></td>" &
                "</tr></table>" &

                /* ============ DADOS DA OCORRÊNCIA ============ */
                "<div style='" & _sec & "'>" &
                    "<div style='" & _hsec & "'>DADOS DO ACIONAMENTO</div>" &
                    "<table cellspacing='0' cellpadding='0' style='width:100%;'>" &
                        "<tr>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>ABERTURA</div><div style='" & _val & "'>" & Text(_ac.Data; "[$-pt-BR]dd/mm/yyyy hh:mm") & "</div></td>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>TÉRMINO</div><div style='" & _val & "'>" & If(IsBlank(_ac.Data_termino); "<span style='color:#B98900;'>em andamento</span>"; Text(_ac.Data_termino; "[$-pt-BR]dd/mm/yyyy hh:mm")) & "</div></td>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>RESPONSÁVEL PELO REGISTRO</div><div style='" & _val & "'>" & Coalesce(_ac.Usuario; "—") & "</div></td>" &
                        "</tr>" &
                        "<tr>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>PROTOCOLO</div><div style='" & _val & "'>" & Coalesce(_ac.Protocolo; "—") & "</div></td>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>TIPO DE ACIONAMENTO</div><div style='" & _val & "'>" & Coalesce(_ac.Acionamento; "—") & "</div></td>" &
                            "<td style='" & _tdc & "'><div style='" & _lbl & "'>AMBIENTE</div><div style='" & _val & "'>" & Coalesce(_ac.Ambiente; "—") & "</div></td>" &
                        "</tr>" &
                    "</table>" &
                    "<div style='margin-top:10px;background:#F7F9FB;border-left:3px solid #C9D8E4;padding:10px 12px;'>" &
                        "<div style='" & _lbl & "'>DESCRIÇÃO DA OCORRÊNCIA</div>" &
                        "<div style='font-size:12.5px;color:#22303B;margin-top:4px;'>" & Substitute(Coalesce(_ac.Descricao_da_ocorrencia; "Sem descrição registrada."); "<"; "&lt;") & "</div>" &
                    "</div>" &
                "</div>" &

                /* ============ AERONAVE (só quando houver) ============ */
                If(
                    !IsBlank(_ac.Matricula_aeronave) Or !IsBlank(_ac.Modelo_aeronave);
                    "<div style='" & _sec & "border-top-color:#C05621;'>" &
                        "<div style='" & _hsec & "'>AERONAVE ENVOLVIDA</div>" &
                        "<table cellspacing='0' cellpadding='0' style='width:100%;'>" &
                            "<tr>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>MATRÍCULA</div><div style='" & _val & "'>" & Upper(Coalesce(_ac.Matricula_aeronave; "—")) & "</div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>MODELO</div><div style='" & _val & "'>" & Upper(Coalesce(_ac.Modelo_aeronave; "—")) & "</div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>PESSOAS A BORDO (POB)</div><div style='" & _val & "'>" & Coalesce(Text(_ac.POB); "—") & "</div></td>" &
                            "</tr>" &
                            "<tr>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>COMBUSTÍVEL / AUTONOMIA</div><div style='" & _val & "'>" & Coalesce(Text(_ac.Combustivel_autonomia); "—") & "</div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>PISTA PARA POUSO</div><div style='" & _val & "'>RWY " & Coalesce(Text(_ac.RWY_para_pouso); "—") & "</div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>TEMPO ESTIMADO DE POUSO</div><div style='" & _val & "'>" & Coalesce(Text(_ac.Tempo_estimado_de_Pouso); "—") & " min</div></td>" &
                            "</tr>" &
                            "<tr>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>TIPO DE PANE</div><div style='" & _val & "'>" & Upper(Coalesce(_ac.Tipo_de_pane; "—")) & "</div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>CARGA PERIGOSA</div><div style='margin-top:4px;'><span style='display:inline-block;padding:2px 9px;border-radius:9px;font-size:10px;font-weight:700;background:" & If(_ac.Tem_carga_perigosa; "#A62639"; "#E8EDF2") & ";color:" & If(_ac.Tem_carga_perigosa; "#FFFFFF"; "#22303B") & ";'>" & If(_ac.Tem_carga_perigosa; "SIM"; "NÃO") & "</span></div></td>" &
                                "<td style='" & _tdc & "'><div style='" & _lbl & "'>ACFT MUNICIADA</div><div style='margin-top:4px;'><span style='display:inline-block;padding:2px 9px;border-radius:9px;font-size:10px;font-weight:700;background:" & If(_ac.ACFT_municiada; "#A62639"; "#E8EDF2") & ";color:" & If(_ac.ACFT_municiada; "#FFFFFF"; "#22303B") & ";'>" & If(_ac.ACFT_municiada; "SIM"; "NÃO") & "</span></div></td>" &
                            "</tr>" &
                        "</table>" &
                    "</div>";
                    ""
                ) &

                /* ============ TEMPO DE RESPOSTA POR ATOR ============ */
                "<div style='" & _sec & "border-top-color:#1F7A4D;'>" &
                    "<div style='" & _hsec & "'>TEMPO DE RESPOSTA POR ACIONADO</div>" &
                    If(
                        CountRows(_resp) = 0;
                        "<div style='font-size:12px;color:#8A98A4;padding:10px 0;'>Nenhuma resposta registrada até o momento.</div>";
                        "<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;margin-top:8px;'>" &
                            "<tr style='background:#F2F6F9;'>" &
                                "<th style='text-align:left;padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>ACIONADO</th>" &
                                "<th style='text-align:left;padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>ACIONADO ÀS</th>" &
                                "<th style='text-align:left;padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>RESPOSTA ÀS</th>" &
                                "<th style='text-align:right;padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>TEMPO</th>" &
                                "<th style='text-align:right;padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>PRAZO</th>" &
                            "</tr>" &
                            Concat(
                                Sort(_resp; SegResposta; SortOrder.Ascending) As _q;
                                With(
                                    {
                                        _dentro: _q.Prazo = 0 Or _q.SegResposta <= _q.Prazo * 60;
                                        _tt: If(
                                            _q.SegResposta < 60; Text(_q.SegResposta) & "s";
                                            _q.SegResposta < 3600; Text(RoundDown(_q.SegResposta / 60; 0)) & "m " & Text(Mod(_q.SegResposta; 60)) & "s";
                                            Text(RoundDown(_q.SegResposta / 3600; 0)) & "h " & Text(RoundDown(Mod(_q.SegResposta; 3600) / 60; 0)) & "m"
                                        )
                                    };
                                    "<tr>" &
                                        "<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;font-weight:600;color:#22303B;'>" & Coalesce(_q.Ator; _q.Texto) & If(IsBlank(_q.Nivel); ""; " <span style='font-size:9px;color:#8A98A4;font-weight:600;'>" & _q.Nivel & "</span>") & "</td>" &
                                        "<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;color:#5D6B77;'>" & Text(_q.GatilhoMomento; "[$-pt-BR]hh:mm") & "</td>" &
                                        "<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;color:#5D6B77;'>" & Text(_q.Momento; "[$-pt-BR]hh:mm") & "</td>" &
                                        "<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;text-align:right;'><span style='display:inline-block;padding:2px 9px;border-radius:9px;font-size:11px;font-weight:700;background:" & If(_dentro; "#E3F2E9"; "#FBE7EA") & ";color:" & If(_dentro; "#1F7A4D"; "#A62639") & ";'>" & _tt & "</span></td>" &
                                        "<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;text-align:right;font-size:11px;color:#8A98A4;'>" & If(_q.Prazo = 0; "sem prazo"; Text(_q.Prazo) & " min") & "</td>" &
                                    "</tr>"
                                );
                                ""
                            ) &
                        "</table>"
                    ) &
                "</div>" &

                /* ============ LINHA DO TEMPO ============ */
                "<div style='" & _sec & "border-top-color:#0B2E4F;'>" &
                    "<div style='" & _hsec & "'>LINHA DO TEMPO DAS ATIVIDADES</div>" &
                    "<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;margin-top:10px;'>" &
                    Concat(
                        Sort(_tl; Ordem; SortOrder.Ascending) As _r;
                        With(
                            {
                                _cor: Switch(
                                    _r.Acao;
                                    "ACIONAR"; "#B98900";
                                    "ACIONAR_SOBREAVISO"; "#B98900";
                                    "RESPONDEU AO FLOW"; "#B98900";
                                    "SOBREAVISO"; "#C05621";
                                    "INFORMAR"; "#155E8F";
                                    "NOTIFICADO"; "#A9BCCB";
                                    "CHEGOU"; "#1F7A4D";
                                    "CONTATO_NR"; "#A62639";
                                    "NAO COMPARECERA"; "#A62639";
                                    "ERRO CHAT"; "#A62639";
                                    "SEM RESPOSTA"; "#5D6B77";
                                    "CRIAÇÃO"; "#0B2E4F";
                                    "FINALIZAÇÃO"; "#0B2E4F";
                                    "CHAT"; "#5D6B77";
                                    "ATIVIDADE MANUAL"; "#5D6B77";
                                    "REGISTRO DE VÍTIMA"; "#7A4E82";
                                    "ALTERAÇÃO DE VÍTIMA"; "#7A4E82";
                                    "EXCLUSÃO DE VÍTIMA"; "#7A4E82";
                                    "#5D6B77"
                                );
                                _abTxt: If(
                                    _r.SegAbertura < 60; Text(Max(_r.SegAbertura; 0)) & "s";
                                    _r.SegAbertura < 3600; Text(RoundDown(_r.SegAbertura / 60; 0)) & "m " & Text(Mod(_r.SegAbertura; 60)) & "s";
                                    Text(RoundDown(_r.SegAbertura / 3600; 0)) & "h " & Text(RoundDown(Mod(_r.SegAbertura; 3600) / 60; 0)) & "m"
                                );
                                _antTxt: If(
                                    _r.SegAnterior < 60; Text(Max(_r.SegAnterior; 0)) & "s";
                                    _r.SegAnterior < 3600; Text(RoundDown(_r.SegAnterior / 60; 0)) & "m " & Text(Mod(_r.SegAnterior; 60)) & "s";
                                    Text(RoundDown(_r.SegAnterior / 3600; 0)) & "h " & Text(RoundDown(Mod(_r.SegAnterior; 3600) / 60; 0)) & "m"
                                );
                                _rpTxt: If(
                                    IsBlank(_r.SegResposta); "";
                                    _r.SegResposta < 60; Text(_r.SegResposta) & "s";
                                    _r.SegResposta < 3600; Text(RoundDown(_r.SegResposta / 60; 0)) & "m " & Text(Mod(_r.SegResposta; 60)) & "s";
                                    Text(RoundDown(_r.SegResposta / 3600; 0)) & "h " & Text(RoundDown(Mod(_r.SegResposta; 3600) / 60; 0)) & "m"
                                )
                            };
                            "<tr>" &
                                "<td style='width:88px;padding:0 10px 0 0;text-align:right;vertical-align:top;'>" &
                                    "<div style='font-size:13px;font-weight:700;color:#22303B;'>" & Text(_r.Momento; "[$-pt-BR]hh:mm") & "</div>" &
                                    "<div style='font-size:10px;color:#A2AFB9;'>" & Text(_r.Momento; "[$-pt-BR]dd/mm") & "</div>" &
                                "</td>" &
                                "<td style='width:16px;padding:0;border-left:2px solid #E1E7EC;vertical-align:top;'>" &
                                    "<div style='width:11px;height:11px;background:" & _cor & ";border:2px solid #FFFFFF;border-radius:50%;margin-left:-7px;margin-top:4px;'></div>" &
                                "</td>" &
                                "<td style='padding:0 0 12px 8px;vertical-align:top;'>" &
                                    "<div style='background:#FFFFFF;border:1px solid #E8EDF1;border-left:3px solid " & _cor & ";padding:9px 12px;'>" &
                                        "<span style='display:inline-block;padding:1px 9px;border-radius:9px;background:" & _cor & ";color:" & If(_cor = "#A9BCCB"; "#22303B"; "#FFFFFF") & ";font-size:9.5px;font-weight:700;letter-spacing:.06em;'>" & _r.Acao & "</span>" &
                                        If(IsBlank(_r.Ator); ""; " <span style='font-size:12px;font-weight:700;color:#0B2E4F;'>" & _r.Ator & "</span>") &
                                        If(IsBlank(_r.Nivel); ""; " <span style='font-size:9px;color:#8A98A4;font-weight:600;'>&middot; " & _r.Nivel & "</span>") &
                                        "<div style='font-size:12.5px;color:#22303B;margin-top:5px;'>" & Substitute(_r.Texto; "<"; "&lt;") & "</div>" &
                                        "<div style='margin-top:7px;font-size:10px;color:#8A98A4;'>" &
                                            "<span style='display:inline-block;padding:1px 7px;background:#F2F6F9;color:#5D6B77;font-weight:700;'>T+ " & _abTxt & "</span>" &
                                            If(
                                                _r.Ordem = 1;
                                                "";
                                                " &nbsp;<span style='display:inline-block;padding:1px 7px;background:#F2F6F9;color:#8A98A4;'>intervalo " & _antTxt & "</span>"
                                            ) &
                                            If(
                                                IsBlank(_r.SegResposta);
                                                "";
                                                " &nbsp;<span style='display:inline-block;padding:1px 7px;font-weight:700;background:" & If(_r.Prazo = 0 Or _r.SegResposta <= _r.Prazo * 60; "#E3F2E9"; "#FBE7EA") & ";color:" & If(_r.Prazo = 0 Or _r.SegResposta <= _r.Prazo * 60; "#1F7A4D"; "#A62639") & ";'>RESPOSTA EM " & _rpTxt & If(_r.Prazo = 0; ""; " (prazo " & _r.Prazo & " min)") & "</span>"
                                            ) &
                                        "</div>" &
                                    "</div>" &
                                "</td>" &
                            "</tr>"
                        );
                        ""
                    ) &
                    "</table>" &
                    If(
                        CountRows(_tl) = 0;
                        "<div style='font-size:12px;color:#8A98A4;padding:10px 0;'>Nenhuma atividade registrada para este acionamento.</div>";
                        ""
                    ) &
                "</div>" &

                /* ============ RELATÓRIO FINAL ============ */
                If(
                    IsBlank(_ac.Relatorio_final);
                    "";
                    "<div style='" & _sec & "border-top-color:#1F7A4D;'>" &
                        "<div style='" & _hsec & "'>RELATÓRIO FINAL</div>" &
                        "<div style='font-size:12.5px;color:#22303B;margin-top:8px;'>" & Substitute(_ac.Relatorio_final; "<"; "&lt;") & "</div>" &
                    "</div>"
                ) &

                /* ============ RODAPÉ ============ */
                "<div style='margin-top:12px;padding:10px 4px;border-top:1px solid #E1E7EC;font-size:10px;color:#8A98A4;'>" &
                    "Relatório gerado em " & Text(Now(); "[$-pt-BR]dd/mm/yyyy hh:mm") & " &nbsp;&middot;&nbsp; AIRPORTNOW / REA &nbsp;&middot;&nbsp; " & Coalesce(_ac.Protocolo; "") &
                "</div>" &

                "</div>"
            )
        )
    )
)
```

## Observações

- **Aspas**: todo atributo HTML usa aspas simples, então nenhuma string precisa de escape.
  Se você editar e precisar de aspas duplas dentro do HTML, dobre-as (`""`).
- **Locale**: bloco escrito para a barra de fórmulas pt-BR. Para colar como YAML
  (`.pa.yaml`), trocar `;` de argumento por `,` e `;;` por `;`.
- **Tempo de resposta**: medido do último gatilho do próprio ator
  (`ACIONAR`/`ACIONAR_SOBREAVISO`/`SOBREAVISO`/`INFORMAR`/`NOTIFICADO`) até o retorno dele
  (`CHEGOU`/`RESPONDEU AO FLOW`/`NAO COMPARECERA`/`CONTATO_NR`/`SEM RESPOSTA`).
  A cor do chip compara com `Prazo_de_chegada_em_minutos` da entidade/equipamento.
